"""
Enemy classes for PyDoom game
"""

from cmu_graphics import Image
from dataclasses import dataclass
import math
from image_utils import get_png_dimensions

@dataclass
class SpriteFrame:
    """Class to hold sprite frame data."""
    image: Image
    width: int
    height: int

class Enemy:
    """Base enemy class."""
    
    def __init__(self):
        self.health = 100
        self.x = 0
        self.y = 0
        self.speed = 0.1
        self.angle = 0
        self.visible = False

    def move(self) -> None:
        """Update enemy position."""
        pass

    def render(self) -> None:
        """Update enemy visibility."""
        pass

class Imp(Enemy):
    """Imp enemy class."""
    
    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x
        self.y = y
        self.frame_counter = 0
        self.current_frame = 0
        self.frames_per_state = 8
        self.sprites = []
        
        # Load all animation frames with actual dimensions
        for i in range(4):  # frame0 to frame3
            filepath = f'assets/Imp/frame{i}.png'
            width, height = get_png_dimensions(filepath)
            sprite = Image(filepath, self.x, self.y,
                         align='bottom', width=width, height=height, visible=False)
            self.sprites.append(SpriteFrame(sprite, width, height))
        
        self.sprite = self.sprites[0]  # Current visible sprite
        self.visible = False
    
    def update_animation(self) -> None:
        """Update the imp's animation state."""
        if not self.visible:
            return
            
        self.frame_counter += 1
        
        if self.frame_counter >= self.frames_per_state:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            
            # Update current sprite
            self.sprite = self.sprites[self.current_frame]
    
    def move(self) -> None:
        """Update Imp position."""
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.update_animation()
    
    def render(self) -> None:
        """Update Imp visibility."""
        self.sprite.image.visible = self.visible