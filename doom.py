"""
PyDoom - A simple Doom-like game implementation using cmu_graphics. Why may you ask? I havent the foggiest Idea.
"""

from typing import Tuple, Optional
from dataclasses import dataclass
import math
import time
from cmu_graphics import *
import utils
import constants
from enemy import Imp, SpriteFrame
import astar

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

# Add these variables to the top of the file with other game state
shooting = False
current_frame = 0
frame_counter = 0
enemies_current_frame = 0

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

# Load sound effects
sounds = {
    'fire': Sound('assets/firing.mp3'),
    'open': Sound('assets/opening.mp3'),
    'reload': Sound('assets/reloading.mp3'),
    'close': Sound('assets/closing.mp3')
}

# Test enemy
constants.ENEMY_MAP.append(Imp(5.5, 3.5))
# constants.ENEMY_MAP.append(Imp(1, 1))
# constants.ENEMY_MAP.append(Imp(2, 2))
# constants.ENEMY_MAP.append(Imp(1, 2))
# constants.ENEMY_MAP.append(Imp(2, 1))

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
    global shooting, current_frame
    if not shooting:
        shooting = True
        current_frame = 0
        sounds['fire'].play()

def update_weapon_animation() -> None:
    """Update weapon animation state."""
    global shooting, current_frame, frame_counter
    
    if not shooting:
        return
        
    frames_per_state = 8  # Number of frames to show each animation state
    
    # Update frame counter
    frame_counter += 1
    
    if frame_counter >= frames_per_state:
        frame_counter = 0
        current_frame += 1
        
        # Play appropriate sound for current frame
        if current_frame == 1:
            sounds['open'].play()
        elif current_frame == 2:
            sounds['reload'].play()
        elif current_frame == 4:
            sounds['close'].play()
    
    # Hide all frames
    for frame in weapon_frames.values():
        frame.visible = False
    
    # Show current frame
    if current_frame == 0:
        weapon_frames['frame0'].visible = True
    elif current_frame == 1:
        weapon_frames['frame1'].visible = True
    elif current_frame == 2:
        weapon_frames['frame2'].visible = True
    elif current_frame == 3:
        weapon_frames['frame2'].visible = True  # Keep frame2 visible during reload
    else:
        # Aaaaaaaand we're done!
        weapon_frames['frame0'].visible = True
        shooting = False

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

def calculate_sprite_dimensions(distance: float, sprite_frame: SpriteFrame) -> Tuple[float, float]:
    """Calculate sprite dimensions based on distance and actual sprite dimensions.
    
    Args:
        distance: Distance to sprite
        sprite_frame: Current sprite frame with actual dimensions
        
    Returns:
        Tuple of (height, width) 
    """
    aspect_ratio = sprite_frame.width / sprite_frame.height
    height = SCREEN_HEIGHT / (distance + 0.0001)  # Avoid division by zero
    width = height * aspect_ratio
    return height, width

def render_sprite(sprite: Imp) -> Optional[dict]:
    """Render a sprite with billboarding.
    
    Args:
        sprite: The sprite to render
        
    Returns:
        Dictionary with sprite rendering information or None if sprite shouldn't be rendered
    """
    if not sprite.visible:
        return None
    
    # Calculate sprite position relative to player, with 0.5 offset for chunk centering
    dx = (sprite.x + 0.5) - player.x
    dy = (sprite.y + 0.5) - player.y
    
    # Calculate euclidean distance
    euclidean_distance = math.sqrt(dx * dx + dy * dy)
    
    if euclidean_distance < 0.1 or euclidean_distance > MAX_VIEW_DISTANCE:
        return None
    
    # Calculate angle to sprite relative to player's view direction
    sprite_angle = math.atan2(dy, dx)
    relative_angle = sprite_angle - player.angle
    
    # Normalize angle to [-pi, pi]
    while relative_angle > math.pi:
        relative_angle -= 2 * math.pi
    while relative_angle < -math.pi:
        relative_angle += 2 * math.pi
    
    # Check if sprite is in field of view
    if abs(relative_angle) > math.pi / 2:
        return None
    
    # Calculate screen position
    fov = math.pi / 2  # 90 degrees field of view
    screen_x = SCREEN_WIDTH * (0.5 + math.tan(relative_angle) / (2 * math.tan(fov / 2)))
    
    # Calculate corrected distance for fisheye
    corrected_distance = euclidean_distance * math.cos(relative_angle)
    
    # Calculate sprite dimensions
    height, width = calculate_sprite_dimensions(corrected_distance, sprite.sprite)
    screen_y = SCREEN_HEIGHT / 2
    
    # Calculate sprite corners
    half_width = width / 2
    half_height = height / 2
    
    vertices = [
        (screen_x - half_width, screen_y - half_height),
        (screen_x + half_width, screen_y - half_height),
        (screen_x + half_width, screen_y + half_height),
        (screen_x - half_width, screen_y + half_height)
    ]
    
    # Hide all sprite frames except current one
    for s in sprite.sprites:
        s.image.visible = False
    sprite.sprite.image.visible = True
    
    return {
        'type': 'sprite',
        'distance': corrected_distance,
        'vertices': vertices,
        'sprite': sprite
    }

def run_world() -> None:
    """Render the 3D world view with proper depth sorting."""
    render_elements = []
    
    for column in range(0, SCREEN_WIDTH, RESOLUTION):
        column_angle = player.angle - (math.atan(0.5 - (column + 0.5) / (SCREEN_WIDTH / 2)))
        distance = ray_cast(column_angle)
        
        if distance is not None:
            wall_top, wall_bottom = calculate_wall_dimensions(distance, column_angle)
            
            render_elements.append({
                'type': 'floor',
                'distance': MAX_VIEW_DISTANCE,  
                'vertices': [
                    (column, wall_bottom),
                    (column + RESOLUTION, wall_bottom),
                    (column + RESOLUTION, SCREEN_HEIGHT),
                    (column, SCREEN_HEIGHT)
                ],
                'color': constants.PosColor.EMPTY.color()
            })
            
            render_elements.append({
                'type': 'wall',
                'distance': distance,
                'vertices': [
                    (column, wall_top),
                    (column + RESOLUTION, wall_top),
                    (column + RESOLUTION, wall_bottom),
                    (column, wall_bottom)
                ],
                'color': constants.PosColor.LIGHTWALL.color() #TODO: Fix wall color logic, (allow multiple colors)
            })
    
    # Update and render sprites
    
    for enemy in constants.ENEMY_MAP:    
        enemy.update_animation()
        sprite_element = render_sprite(enemy)
        if sprite_element:
            render_elements.append(sprite_element)
        
        render_elements.sort(key=lambda x: -x['distance'])
        
        current_screen.clear()
        
        background_group = Group()  
        sprite_group = Group()      
        wall_group = Group()        
        
        current_screen.add(background_group)
        current_screen.add(sprite_group)
        current_screen.add(wall_group)
        
        if sprite_element:
            sprite = sprite_element['sprite']
            current_frame = sprite.sprite.image
            current_frame.centerX = int((sprite_element['vertices'][0][0] + sprite_element['vertices'][1][0]) / 2)
            current_frame.centerY = int((sprite_element['vertices'][0][1] + sprite_element['vertices'][2][1]) / 2)
            current_frame.width = sprite_element['vertices'][1][0] - sprite_element['vertices'][0][0] + 0.1
            current_frame.height = sprite_element['vertices'][2][1] - sprite_element['vertices'][0][1] + 0.1
            sprite_group.add(current_frame)
    
    for element in render_elements:
        if element['type'] == 'sprite':
            continue  
        
        shape = Polygon(*[coord for vertex in element['vertices'] for coord in vertex], 
                      fill=element['color'])
        
        if element['type'] == 'floor':
            background_group.add(shape)
        else:  
            if sprite_element and element['distance'] > sprite_element['distance']:
                background_group.add(shape)
            else:
                wall_group.add(shape)
    
    background_group.toBack()
    sprite_group.toFront()
    wall_group.toFront()
    
def move_enemies():
    """Movies all enemies that can move towards the player every 60 frames (roughly once per second)."""
    global enemies_current_frame
    
    enemies_current_frame += 1
    if enemies_current_frame % 10 != 0:
        return
    print(f"player at {player.x} {player.y}")
    for enemy in constants.ENEMY_MAP:
        path = astar.find_path((enemy.x, enemy.y), (player.x, player.y))
        if not path or len(path) < 2:
            print("no path")
            print(f"for pos {enemy.x} {enemy.y}")
            continue
        enemy.move_to(path[1])

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
    run_world()
    update_weapon_animation()
    move_enemies()

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