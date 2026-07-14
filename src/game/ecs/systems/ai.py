from ..components import Position, Actor, AI, Attacks
from .combat import clear_terrain_line, fire_ranged
from .movement import try_move

def _adjacent(ax, ay, bx, by):
    return max(abs(ax - bx), abs(ay - by)) == 1

def _sign(n):
    return (n > 0) - (n < 0)

def _move_towards(world, eid, tx, ty, game_map, log):
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

def take_monster_turns(world, game_map, player_eid, log):
    ppos = world.get(Position, player_eid)
    if not ppos: return
    # sort sentient ents by distance from player (closest go first)
    batch = []
    for eid, pos, _ in world.view(Position, Actor):
        if pos.z != game_map.z: continue
        if eid == player_eid: continue
        if not world.has(eid, AI): continue
        batch.append((eid, pos))
    batch.sort(key=lambda t: max(
        abs(t[1].x - ppos.x), abs(t[1].y - ppos.y)
    ))
    for eid, pos in batch:
        if eid == player_eid: continue
        if not world.has(eid, AI): continue
        if _adjacent(pos.x, pos.y, ppos.x, ppos.y):
            dx, dy = ppos.x - pos.x, ppos.y - pos.y
            try_move(world, eid, dx, dy, game_map, log=log)
            continue
        attacks = world.get(Attacks, eid)
        has_ranged_group = bool(
            attacks and attacks.groups.get("ranged")
        )
        if has_ranged_group:
            can_see_player = game_map.visible[pos.x, pos.y]
            clear_shot = clear_terrain_line(
                game_map, pos.x, pos.y, ppos.x, ppos.y
            )
            if can_see_player and clear_shot:
                fire_ranged(
                    world, game_map, eid, ppos.x, ppos.y, log=log
                )
            else:
                _move_towards(
                    world, eid, ppos.x, ppos.y, game_map, log=log
                )
            continue
        # try to move towards player if player visible
        if not game_map.visible[pos.x, pos.y]: continue
        _move_towards(world, eid, ppos.x, ppos.y, game_map,
                      log=log)
