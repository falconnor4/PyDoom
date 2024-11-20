"""
Enemy classes for PyDoom game
"""

from cmu_graphics import Image
import math

class Enemy:
    def __init__(self):
        self.health = 100
        self.x = 0
        self.y = 0
        self.angle = 0
        self.speed = 0.1
        self.visible = False

    def move(self) -> None:
        """Update enemy position."""
        pass

    def render(self) -> None:
        """Update enemy visibility."""
        pass

class Imp(Enemy):
    """Enemy class representing an Imp monster."""
    
    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x
        self.y = y
        self.sprite = Image('assets/Imp/frame0.png', self.x, self.y,
                          align='bottom', width=328, height=488, visible=False)
    
    def move(self) -> None:
        """Update Imp position."""
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.sprite.x = self.x
        self.sprite.y = self.y
    
    def render(self) -> None:
        """Update Imp visibility."""
        self.sprite.visible = self.visible