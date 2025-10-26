from ..components import Position

def move(world, eid, dx, dy, is_blocked):
    pos = world.get(Position, eid)
    if not pos: return
    nx, ny = pos.x + dx, pos.y + dy
    if not is_blocked(nx, ny):
        pos.x, pos.y = nx, ny
