from ..components import Position
from .combat import melee

def try_move(world, eid, dx, dy, game_map, log=None):
    pos = world.get(Position, eid)
    nx, ny = pos.x + dx, pos.y + dy

    if game_map.blocked(nx, ny):
        target = game_map.entity_at.get((nx, ny))
        if target is not None:
            return melee(world, eid, target, log=log)
        elif game_map.doors_closed[nx, ny]:
            game_map.open_door(nx, ny)
        return False
    else:
        pos.x, pos.y = nx, ny
        return True
