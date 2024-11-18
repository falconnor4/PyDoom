import constants

def pack(pos):
    return pos[0] * constants.MAP_DIMENSIONS + pos[1]

def unpack(packed):
    return (packed // constants.MAP_DIMENSIONS, packed % constants.MAP_DIMENSIONS)