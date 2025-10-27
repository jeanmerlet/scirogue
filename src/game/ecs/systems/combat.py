from ..components import *

def die(world, game_map, target, log=None):
    if log:
        dn = world.get(Name, target).text if world.get(Name, target) else "target"
        log.append(f"{dn} dies.")
    renderable = world.get(Renderable, target)
    renderable.ch = "%"
    renderable.order = 0
    pos = world.get(Position, target)
    game_map.entities[pos.x, pos.y] = -1
    world.remove(target, Blocks)
    world.remove(target, AI)

def melee(world, game_map, attacker, target, log=None):
    af = world.get(Faction, attacker)
    df = world.get(Faction, target)
    if af == df: return False
    atk = world.get(Attack, attacker)
    if not atk: return False # fix with log
    dhp = world.get(HP, target)
    if not dhp: return False # fix with log

    dmg = atk.damage
    dhp.current = max(0, dhp.current - dmg)

    if log:
        an = world.get(Name, attacker).text if world.get(Name, attacker) else "Something"
        dn = world.get(Name, target).text if world.get(Name, target) else "target"
        log.append(f"{an} hits {dn} for {dmg}.")
    
    if dhp.current <= 0: die(world, game_map, target, log)
    return True

