from ..components import Position, Actor, AI
from .movement import try_move

def _adjacent(ax, ay, bx, by):
    return max(abs(ax - bx), abs(ay - by)) == 1

def _sign(n):
    return (n > 0) - (n < 0)

def _move_towards(world, eid, tx, ty, game_map, log=None):
    pos = world.get(Position, eid)
    dx = _sign(tx - pos.x)
    dy = _sign(ty - pos.y)
    # try diagonal, then horizontal, then vertical
    candidates = []
    if dx or dy:
        candidates.append((dx, dy))
        if dx: candidates.append((dx, 0))
        if dy: candidates.append((0, dy))
    for cx, cy in candidates:
        if try_move(world, eid, cx, cy, game_map, log=log):
            return True
    return False

def take_monster_turns(world, game_map, player_eid, log=None):
    ppos = world.get(Position, player_eid)
    if not ppos: return
    for eid, pos, _ in world.view(Position, Actor):
        if eid == player_eid: continue
        if not world.has(eid, AI): continue
        if _adjacent(pos.x, pos.y, ppos.x, ppos.y):
            dx, dy = ppos.x - pos.x, ppos.y - pos.y
            try_move(world, eid, dx, dy, game_map, log=log)
            continue
        # try to move towards player if player visible
        if not game_map.visible[pos.x, pos.y]: continue
        _move_towards(world, eid, ppos.x, ppos.y, game_map,
                      log=log)
