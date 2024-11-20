"""
PyDoom - A simple Doom-like game implementation using cmu_graphics
"""

from typing import Tuple, Optional
import math
import time
from dataclasses import dataclass
from cmu_graphics import *
import utils
import constants
from enemy import Imp

# General Game Config
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 360
RESOLUTION = 3
SPEED = 0.9
INITIAL_HEALTH = 99
WALL_HEIGHT_MOD = 2
PLAYER_HEIGHT_MOD = 2
ANIM_BUFFER = 0.1
MAX_VIEW_DISTANCE = 20

@dataclass
class PlayerState:
    x: float = 1.5
    y: float = 1.5
    angle: float = 0.0
    health: int = INITIAL_HEALTH

# Initialize game state
player = PlayerState()
current_screen = Group()
app.stepsPerSecond = 30
app.setMaxShapeCount(69000000)

# Load game assets
hud = Image('assets/DOOM_HUD.png', 0, 360, width=SCREEN_WIDTH, height=40)
background = Image('assets/Loopedskies.png', 0, 0, width=1600, height=200, align='top')
background.toBack()

# Test enemy
test_imp = Imp(5.5, 3.5)  # Place imp in the world
test_imp.visible = True

# Weapon animation frames
weapon_frames = {
    'frame0': Image('assets/SS0.png', 200, 360, align='bottom', width=74, height=69, visible=True),
    'frame1': Image('assets/SS1.png', 200, 360, align='bottom', width=102, height=100, visible=False),
    'frame2': Image('assets/SS2.png', 200, 360, align='bottom', width=252, height=79, visible=False),
    'frame3': Image('assets/SS3.png', 200, 360, align='bottom', width=110, height=64, visible=False),
    'frame4': Image('assets/SS4.png', 200, 360, align='bottom', width=102, height=100, visible=False)
}

def shoot() -> None:
    """Handle weapon shooting animation and sound effects."""
    sounds = {
        'fire': Sound('assets/firing.mp3'),
        'open': Sound('assets/opening.mp3'),
        'reload': Sound('assets/reloading.mp3'),
        'close': Sound('assets/closing.mp3')
    }
    
    animation_sequence = [
        ('fire', 'frame1'),
        ('open', 'frame2'),
        ('reload', 'frame3'),
        ('close', 'frame4'),
    ]
    
    for sound_key, frame_key in animation_sequence:
        sounds[sound_key].play()
        weapon_frames['frame0'].visible = False
        weapon_frames[frame_key].visible = True
        time.sleep(ANIM_BUFFER)
        weapon_frames[frame_key].visible = False
    
    weapon_frames['frame0'].visible = True

def render_shape(vertices: list[Tuple[float, float]], color: str, shape_type: str = 'quad') -> None:
    """Render a shape (triangle or quad) to the current screen.
    
    Args:
        vertices: List of vertex coordinates
        color: Fill color for the shape
        shape_type: Either 'quad' or 'tri'
    """
    if shape_type == 'quad' and len(vertices) == 4:
        shape = Polygon(*[coord for vertex in vertices for coord in vertex], fill=color)
    elif shape_type == 'tri' and len(vertices) == 3:
        shape = Polygon(*[coord for vertex in vertices for coord in vertex], fill=color)
    else:
        raise ValueError(f"Invalid shape type or number of vertices: {shape_type}, {len(vertices)}")
    
    current_screen.add(shape)

def calculate_wall_dimensions(distance: float, column_angle: float) -> Tuple[int, int]:
    """Calculate wall dimensions based on distance and angle.
    
    Args:
        distance: Distance to wall
        column_angle: Angle of the current column
        
    Returns:
        Tuple of (wall_top, wall_bottom) coordinates
    """
    distance *= math.cos(player.angle - column_angle)
    wall_height = min(SCREEN_HEIGHT, int(SCREEN_HEIGHT / distance))
    
    wall_top = max(0, SCREEN_HEIGHT // 2 - wall_height // WALL_HEIGHT_MOD)
    wall_bottom = min(SCREEN_HEIGHT, SCREEN_HEIGHT // 2 + wall_height // PLAYER_HEIGHT_MOD)
    
    return wall_top, wall_bottom

def calculate_sprite_dimensions(distance: float) -> Tuple[int, int]:
    """Calculate sprite dimensions based on distance from player.
    
    Args:
        distance: Distance to sprite
        
    Returns:
        Tuple of (sprite_height, sprite_width)
    """
    base_height = SCREEN_HEIGHT // 3  # Base sprite height at distance 1
    height = min(SCREEN_HEIGHT, int(base_height / distance))
    width = height  # Maintain aspect ratio
    return height, width

def get_sprite_screen_pos(world_x: float, world_y: float) -> Tuple[float, float, float]:
    """Calculate sprite's screen position and distance.
    
    Args:
        world_x: Sprite's world X coordinate
        world_y: Sprite's world Y coordinate
        
    Returns:
        Tuple of (screen_x, screen_y, distance)
    """
    # Calculate relative position to player
    dx = world_x - player.x
    dy = world_y - player.y
    
    # Calculate distance
    distance = math.sqrt(dx * dx + dy * dy)
    
    # Calculate angle between player's view and sprite
    sprite_angle = math.atan2(dx, dy)
    relative_angle = sprite_angle - player.angle
    
    # Normalize angle
    while relative_angle > math.pi:
        relative_angle -= 2 * math.pi
    while relative_angle < -math.pi:
        relative_angle += 2 * math.pi
        
    # Calculate screen position
    fov = math.pi / 3  # 90 degrees field of view
    screen_x = SCREEN_WIDTH * (0.5 + relative_angle / fov)
    
    # Calculate vertical position based on distance
    sprite_height, _ = calculate_sprite_dimensions(distance)
    screen_y = SCREEN_HEIGHT // 2  # Center vertically
    
    return screen_x, screen_y, distance

def render_sprite(sprite: Imp) -> Optional[dict]:
    """Render a sprite with billboarding.
    
    Args:
        sprite: The sprite to render
        
    Returns:
        Dictionary with sprite rendering information or None if sprite shouldn't be rendered
    """
    if not sprite.visible:
        return None
        
    # Calculate relative position to player
    dx = sprite.x - player.x
    dy = sprite.y - player.y
    
    # Calculate distance using Euclidean distance
    distance = math.sqrt(dx * dx + dy * dy)
    
    # Check if sprite is in view
    if distance < 0.1 or distance > MAX_VIEW_DISTANCE:
        return None
    
    # Calculate angle to sprite relative to player's view
    sprite_angle = math.atan2(dy, dx) - player.angle
    
    # Normalize angle to [-π, π] #TODO: Fix
    while sprite_angle > math.pi:
        sprite_angle -= math.pi*2
    while sprite_angle < -math.pi:
        sprite_angle += math.pi*2
        
    # Check if sprite is in field of view (90 degrees = π/2)
    if abs(sprite_angle) > math.pi / 2:
        return None
    
    # Project sprite position onto screen
    screen_x = SCREEN_WIDTH / 2 + math.tan(sprite_angle) * SCREEN_WIDTH
    
    # Calculate sprite dimensions
    height, width = calculate_sprite_dimensions(distance)
    
    # Calculate screen y (vertical center)
    screen_y = SCREEN_HEIGHT / 2
    
    # Create vertices for sprite quad
    half_width = width / 2
    half_height = height / 2
    
    vertices = [
        (screen_x - half_width, screen_y - half_height),  # Top left
        (screen_x + half_width, screen_y - half_height),  # Top right
        (screen_x + half_width, screen_y + half_height),  # Bottom right
        (screen_x - half_width, screen_y + half_height)   # Bottom left
    ]
    
    return {
        'type': 'sprite',
        'distance': distance,
        'vertices': vertices,
        'sprite': sprite
    }

def render_world() -> None:
    """Render the 3D world view with proper depth sorting."""
    # List to store all renderable elements with their distances
    render_elements = []
    
    # First pass: Collect all wall segments and their distances
    for column in range(0, SCREEN_WIDTH, RESOLUTION):
        column_angle = player.angle - (math.atan(0.5 - (column + 0.5) / (SCREEN_WIDTH / 2)))
        distance = ray_cast(column_angle)
        
        if distance is not None:
            wall_top, wall_bottom = calculate_wall_dimensions(distance, column_angle)
            
            # Store floor segment
            render_elements.append({
                'type': 'floor',
                'distance': MAX_VIEW_DISTANCE,  # Floor is always furthest
                'vertices': [
                    (column, wall_bottom),
                    (column + RESOLUTION, wall_bottom),
                    (column + RESOLUTION, SCREEN_HEIGHT),
                    (column, SCREEN_HEIGHT)
                ],
                'color': constants.PosColor.EMPTY.color()
            })
            
            # Store wall segment
            render_elements.append({
                'type': 'wall',
                'distance': distance,
                'vertices': [
                    (column, wall_top),
                    (column + RESOLUTION, wall_top),
                    (column + RESOLUTION, wall_bottom),
                    (column, wall_bottom)
                ],
                'color': constants.PosColor.LIGHTWALL.color()
            })
    
    # Add sprites to render list
    sprite_element = render_sprite(test_imp)
    if sprite_element:
        render_elements.append(sprite_element)
    
    # Sort elements by distance (furthest first)
    render_elements.sort(key=lambda x: -x['distance'])
    
    # Second pass: Render all elements in sorted order
    current_screen.clear()
    
    # Create groups for different layers
    background_group = Group()  # Furthest (floors)
    sprite_group = Group()      # Middle (sprites)
    wall_group = Group()        # Nearest (walls)
    
    current_screen.add(background_group)
    current_screen.add(sprite_group)
    current_screen.add(wall_group)
    
    # Update sprite position
    if sprite_element:
        sprite = sprite_element['sprite']
        sprite.sprite.centerX = (sprite_element['vertices'][0][0] + sprite_element['vertices'][0][1]) / 2
        sprite.sprite.centerY = (sprite_element['vertices'][0][1] + sprite_element['vertices'][2][1]) / 2
        sprite.sprite.width = sprite_element['vertices'][1][0] - sprite_element['vertices'][0][0]
        sprite.sprite.height = sprite_element['vertices'][2][1] - sprite_element['vertices'][0][1]
        sprite.sprite.visible = True
        sprite_group.add(sprite.sprite)
    
    # Render elements in their appropriate groups
    for element in render_elements:
        if element['type'] == 'sprite':
            continue  # Already handled above
        
        shape = Polygon(*[coord for vertex in element['vertices'] for coord in vertex], 
                      fill=element['color'])
        
        if element['type'] == 'floor':
            background_group.add(shape)
        else:  # wall
            if sprite_element and element['distance'] > sprite_element['distance']:
                background_group.add(shape)
            else:
                wall_group.add(shape)
    
    # Ensure proper group ordering
    background_group.toBack()
    sprite_group.toFront()
    wall_group.toFront()

def ray_cast(angle: float) -> Optional[float]:
    """Cast a ray and return the distance to the nearest wall.
    
    Args:
        angle: Angle of the ray
        
    Returns:
        Distance to wall or None if no wall found
    """
    distance = 0
    while distance < MAX_VIEW_DISTANCE:
        distance += RESOLUTION * 0.00625
        
        test_x = int(player.x + distance * math.cos(angle))
        test_y = int(player.y + distance * math.sin(angle))
        
        if not utils.is_inside_map((test_x, test_y)):
            return MAX_VIEW_DISTANCE
            
        if constants.MAP[test_y][test_x].is_impassible():
            return distance
            
    return None

def is_collision(x: float, y: float) -> bool:
    """Check if a position would result in a collision.
    
    Args:
        x: X coordinate to check
        y: Y coordinate to check
        
    Returns:
        True if position would result in collision, False otherwise
    """
    grid_x, grid_y = int(x), int(y)
    
    if not utils.is_inside_map((grid_x, grid_y)):
        return True
    return constants.MAP[grid_y][grid_x].is_impassible()

def handle_movement(keys: set) -> None:
    """Handle player movement based on keyboard input.
    
    Args:
        keys: Set of currently held keys
    """
    new_x, new_y = player.x, player.y
    
    if 'w' in keys:
        new_x += SPEED * math.cos(player.angle) * 0.1
        new_y += SPEED * math.sin(player.angle) * 0.1
    if 's' in keys:
        new_x -= SPEED * math.cos(player.angle) * 0.1
        new_y -= SPEED * math.sin(player.angle) * 0.1
    if 'a' in keys:
        new_x += SPEED * math.sin(player.angle) * 0.1
        new_y -= SPEED * math.cos(player.angle) * 0.1
    if 'd' in keys:
        new_x -= SPEED * math.sin(player.angle) * 0.1
        new_y += SPEED * math.cos(player.angle) * 0.1
        
    if not is_collision(new_x, new_y):
        player.x, player.y = new_x, new_y

def handle_rotation(keys: set) -> None:
    """Handle player rotation based on keyboard input.
    
    Args:
        keys: Set of currently held keys
    """
    if 'left' in keys:
        player.angle = (player.angle - math.pi/16) % (math.pi * 2)
        background.centerX = player.angle * -63.661 + 200
    if 'right' in keys:
        player.angle = (player.angle + math.pi/16) % (math.pi * 2)
        background.centerX = player.angle * -63.661 + 200

def onStep() -> None:
    """Game update function called every frame."""
    current_screen.clear()
    render_world()

def onKeyHold(keys: set) -> None:
    """Handle keyboard input.
    
    Args:
        keys: Set of currently held keys
    """
    handle_movement(keys)
    handle_rotation(keys)
    
    if 'space' in keys:
        shoot()

if __name__ == '__main__':
    cmu_graphics.run()