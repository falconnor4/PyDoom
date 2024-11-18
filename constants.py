from enum import Enum

ADJACENT_OFFSETS = [
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
]

MAP_DIMENSIONS = 10
class PosColor(Enum):
    EMPTY = 0
    LIGHTWALL = 1
    DARKWALL = 2
    Portal = 3

    def is_impassible(self):
        if self == PosColor.EMPTY:
            return False
        return True
    
    # cost for pathfinding
    def cost(self):
        if self == PosColor.EMPTY:
            return 1
        return None
    
    def color(self):
        return COLOR_MAP[self]

COLOR_MAP = {
    PosColor.EMPTY: 'firebrick',
    PosColor.LIGHTWALL: 'gray',
    PosColor.DARKWALL: 'dimGray',
    PosColor.Portal: 'lime',
}
MAP = [
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.DARKWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.DARKWALL, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.DARKWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.DARKWALL, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.EMPTY, PosColor.LIGHTWALL],
    [PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL, PosColor.LIGHTWALL],
]