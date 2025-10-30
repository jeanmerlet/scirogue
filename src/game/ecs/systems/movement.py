from ..components import Position, Blocks, Name
from .combat import melee

def try_move(world, eid, dx, dy, game_map, log):
    pos = world.get(Position, eid)
    name = world.get(Name, eid).text
    nx, ny = pos.x + dx, pos.y + dy
    if game_map.blocked(nx, ny):
        target = game_map.actors[nx, ny]
        if target >= 0:
            return melee(world, game_map, eid, target, log=log)
        elif game_map.doors_closed[nx, ny]:
            game_map.open_door(nx, ny)
            if name == "player": log.add("You open a door.")
            return True
        elif game_map.walls[nx, ny]:
            if name == "player": log.add("You run into a wall.")
            return False
    else:
        if world.has(eid, Blocks):
            game_map.actors[pos.x, pos.y] = -1
            game_map.actors[nx, ny] = eid
        pos.x, pos.y = nx, ny
        return True
