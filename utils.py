import constants
import struct
from typing import Tuple

def pack(pos):
    return pos[0] * constants.MAP_DIMENSIONS + pos[1]

def unpack(packed):
    return (packed // constants.MAP_DIMENSIONS, packed % constants.MAP_DIMENSIONS)

def distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def is_inside_map(pos):
    return pos[0] >= 0 and pos[0] < constants.MAP_DIMENSIONS and pos[1] >= 0 and pos[1] < constants.MAP_DIMENSIONS