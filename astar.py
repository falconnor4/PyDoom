from numpy import Infinity
import constants
import utils
from sortedcontainers import SortedDict

def find_path(from_pos, to):
    from_pos = (int(from_pos[0]), int(from_pos[1]))
    to = (int(to[0]), int(to[1]))
    
    goals = set()
    goals.add(utils.pack(from_pos))

    visited = set()
    visited.add(utils.pack(from_pos))

    costs = {}
    for x in range(constants.MAP_DIMENSIONS):
        for y in range(constants.MAP_DIMENSIONS):
            costs[utils.pack((x, y))] = constants.MAP[x][y].cost()

    from_positions = {}

    open_set = SortedDict()
    open_set[utils.pack(from_pos)] = g_score(from_pos, goals)

    while len(open_set) > 0:
        pos = open_set.popitem(0)

        for offset in constants.ADJACENT_OFFSETS:
            adj_pos = (pos[0] + offset[0], pos[1] + offset[1])

            packed = utils.pack(adj_pos)
            from_positions[packed] = pos

            if not utils.is_inside_map(adj_pos):
                continue

            path = construct_path(adj_pos, from_positions)
            if packed in goals:
                return path

            if adj_pos == to:
                continue

            if costs[packed] == None:
                continue

            score = len(path) + g_score(adj_pos, from_positions, goals)
            open_set[packed] = score
    return None

def f_score(pos, from_positions, goals):
    h_score(pos, from_positions) + g_score(pos, goals)

def h_score(pos, from_positions):
    return len(construct_path(pos, from_positions))

def g_score(pos, goals):
    min_score = Infinity
    for goal in goals:
        goal_pos = utils.unpack(goal)
        min_score = utils.distance(pos, goal_pos)

    return min_score

def construct_path(to, from_positions):
    path = []
    previous = to

    while from_positions[utils.pack(previous)]:
        pos = from_positions[utils.pack(previous)]
        
        path.append(pos)
        previous = pos

    return path