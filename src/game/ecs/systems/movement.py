from ..components import Position

def move(world, eid, dx, dy, doors_closed, open_door, is_blocked):
    pos = world.get(Position, eid)
    nx, ny = pos.x + dx, pos.y + dy
    if is_blocked(nx, ny):
        if doors_closed[nx, ny]: open_door(nx, ny)
        return
    else:
        pos.x, pos.y = nx, ny
