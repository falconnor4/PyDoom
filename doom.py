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
import enemy

# Game Configuration
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 360
RESOLUTION = 3
SPEED = 0.9
INITIAL_HEALTH = 89
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

def render_world() -> None:
    """Render the 3D world view."""
    for column in range(0, SCREEN_WIDTH, RESOLUTION):
        column_angle = player.angle - (math.atan(0.5 - (column + 0.5) / (SCREEN_WIDTH / 2)))
        distance = ray_cast(column_angle)
        
        if distance is not None:
            wall_top, wall_bottom = calculate_wall_dimensions(distance, column_angle)
            
            # Render floor
            render_shape([
                (column, wall_bottom),
                (column + RESOLUTION, wall_bottom),
                (column + RESOLUTION, SCREEN_HEIGHT),
                (column, SCREEN_HEIGHT)
            ], constants.PosColor.EMPTY.color())
            
            # Render wall
            render_shape([
                (column, wall_top),
                (column + RESOLUTION, wall_top),
                (column + RESOLUTION, wall_bottom),
                (column, wall_bottom)
            ], constants.PosColor.LIGHTWALL.color())

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

class Imp:
    """Enemy class representing an Imp monster."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0.1
        self.health = 100
        self.visible = False
        self.sprite = Image('assets/imp1.png', self.x, self.y,
                          align='bottom', width=100, height=100, visible=False)
    
    def move(self) -> None:
        """Update Imp position."""
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.sprite.x = self.x
        self.sprite.y = self.y
    
    def render(self) -> None:
        """Update Imp visibility."""
        self.sprite.visible = self.visible

if __name__ == '__main__':
    cmu_graphics.run()