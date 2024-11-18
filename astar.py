import constants
import utils

def find_path(from_pos, to, map):
    goals = set()
    goals.add(from_pos)

    costs = {}
    for x in constants.MAP_DIMENSIONS:
        for y in constants.MAP_DIMENSIONS:
            costs[utils.pack((x, y))] = map[x][y].cost()

    from_positions = {}

    generation = [from_pos]

    if len(generation) > 0:
        next_generation = []

        for pos in generation.pop():
            for offset in constants.ADJACENT_OFFSETS:
                adj_pos = (pos[0] + offset[0], pos[1] + offset[1])

                if adj_pos == to:
                    return [adj_pos]

                if adj_pos in costs:
                    continue

                next_generation.append(adj_pos)
                from_positions[pos] = adj_pos

        generation = next_generation

def f_score():
    pass

def g_score():
    pass

def construct_path(to, from_positions):
    path = []
    previous = to

    for pos in from_positions[pack(previous)]:
        
        path.append(pos)
        previous = pos

    return path