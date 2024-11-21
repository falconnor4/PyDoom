import constants
import utils
from sortedcontainers import SortedDict

def find_path(from_pos, to):
    """Returns a path from one positino to another using A* search. if no path is finds it returns None."""
    from_pos = (int(from_pos[0]), int(from_pos[1]))
    to = (int(to[0]), int(to[1]))
    
    goals = set()
    goals.add(utils.pack(to))

    costs = {}
    for x in range(constants.MAP_DIMENSIONS):
        for y in range(constants.MAP_DIMENSIONS):
            costs[utils.pack((x, y))] = constants.MAP[x][y].cost()

    visited = set()
    visited.add(utils.pack(from_pos))

    from_positions = {}

    open_set = SortedDict()
    open_set[utils.pack(from_pos)] = g_score(from_pos, goals)

    while len(open_set) > 0:
        unpacked_pos = open_set.popitem(0)
        pos = utils.unpack(unpacked_pos[0])

        for offset in constants.ADJACENT_OFFSETS:
            adj_pos = (pos[0] + offset[0], pos[1] + offset[1])

            packed = utils.pack(adj_pos)
            
            if packed in visited:
                continue
            
            visited.add(packed)

            if not utils.is_inside_map(adj_pos):
                continue
            
            if adj_pos == from_pos:
                continue

            if packed in goals:
                from_positions[packed] = pos
                return construct_path(adj_pos, from_positions)

            if costs[packed] == None:
                continue

            score = f_score(adj_pos, from_positions, goals)
            open_set[packed] = score
            from_positions[packed] = pos
    return None

def f_score(pos, from_positions, goals):
    h_score(pos, from_positions) + g_score(pos, goals)

def h_score(pos, from_positions):
    return len(construct_path(pos, from_positions))

def g_score(pos, goals):
    """Finds the g-sore for a position: the nearest distance to a goal"""
    goal_pos = None
    min_score = float('inf')
    for goal in goals:
        goal_pos = utils.unpack(goal)
        min_score = min(min_score, utils.distance(pos, goal_pos))

    return min_score

def construct_path(to, from_positions):
    """Returns a constructed path going backwards from the end position to the start position."""
    path = []
    previous = to

    while from_positions.get(utils.pack(previous), None) != None:
        
        pos = from_positions[utils.pack(previous)]
        
        path.append(pos)
        previous = pos
        
    path.reverse()
    return path