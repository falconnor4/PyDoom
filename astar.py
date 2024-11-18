from numpy import Infinity
import constants
import utils
from sortedcontainers import SortedDict

def find_path(from_pos, to, map):
    goals = set()
    goals.add(utils.pack(from_pos))

    visited = set()
    visited.add(utils.pack(from_pos))

    costs = {}
    for x in constants.MAP_DIMENSIONS:
        for y in constants.MAP_DIMENSIONS:
            costs[utils.pack((x, y))] = map[x][y].cost()

    from_positions = {}

    open_set = SortedDict()
    open_set[utils.pack(from_pos)] = f_score(from_pos, from_positions, goals)

    for pos in open_set.pop():

        for offset in constants.ADJACENT_OFFSETS:
            adj_pos = (pos[0] + offset[0], pos[1] + offset[1])

            packed = utils.pack(adj_pos)
            from_positions[packed] = pos

            if not utils.is_inside_map(adj_pos):
                continue

            if packed in goals:
                return construct_path(adj_pos, from_positions)

            if adj_pos == to:
                continue

            if costs[packed] == None:
                continue

            score = f_score()
            open_set.__setitem__(packed, score)
    return None
    

def f_score(pos, from_positions, goals):
    pass

def h_score(pos, from_positions):
    return len(construct_path(pos, from_positions))

def g_score(pos, goals):
    min_score = Infinity
    for goal in goals:
        min_score = utils.distance(pos, goal)
    return min_score

def construct_path(to, from_positions):
    path = []
    previous = to

    for pos in from_positions[utils.pack(previous)]:
        
        path.append(pos)
        previous = pos

    return path