import numpy as np
from ..components import Position, Blocks

def rebuild_occupancy(game_map, world):
    game_map.occupied.fill(False)
    game_map.entity_at = {}
    for eid, pos, _ in world.view(Position, Blocks):
        game_map.occupied[pos.x, pos.y] = True
        game_map.entity_at[(pos.x, pos.y)] = eid
