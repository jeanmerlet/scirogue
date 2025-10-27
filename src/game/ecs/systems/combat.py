from ..components import *

def die(world, game_map, target, log=None):
    renderable = world.get(Renderable, target)
    renderable.ch = "%"
    renderable.order = 0
    pos = world.get(Position, target)
    game_map.entities[pos.x, pos.y] = -1
    world.remove(target, Blocks)
    world.remove(target, AI)
    if log:
        dn = world.get(Name, target).text
        if not dn: dn = "Something"
        if dn == "player":
            log.add(f"You die!")
        else:
            log.add(f"{dn} dies.")

def melee(world, game_map, attacker, target, log=None):
    af = world.get(Faction, attacker).tag
    df = world.get(Faction, target).tag
    if af == df: return False
    atk = world.get(Attack, attacker)
    if not atk: return False
    dhp = world.get(HP, target)
    if not dhp: return False

    dmg = atk.damage
    dhp.current = max(0, dhp.current - dmg)

    if log:
        an = world.get(Name, attacker).text
        dn = world.get(Name, target).text
        if not an: an = "Something"
        if not dn: an = "Something"
        log.add(f"{an} hits {dn} for {dmg}.")
    
    if dhp.current <= 0:
        die(world, game_map, target, log)

    return True

