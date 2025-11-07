from ..components import *

def _calc_attack(world, actor_eid, base_atk):
    eq = world.get(Equipment, actor_eid)
    total = base_atk
    if not eq: return total
    for slot, eid in eq.slots.items():
        if eid is None: continue
        e = world.get(Equippable, eid)
        if e: total += e.attack_bonus
    return total

def die(world, game_map, target, log=None):
    renderable = world.get(Renderable, target)
    renderable.ch = "%"
    renderable.order = 0
    pos = world.get(Position, target)
    game_map.actors[pos.x, pos.y] = -1
    world.remove(target, Blocks)
    world.remove(target, AI)
    if log:
        dn = world.get(Name, target).text
        if not dn: dn = "Something"
        if dn == "player":
            log.add(f"You die!")
        else:
            log.add(f"{dn.capitalize()} dies!")

def melee(world, game_map, attacker, target, log=None):
    af = world.get(Faction, attacker).tag
    df = world.get(Faction, target).tag
    if af == df: return False
    atk = world.get(Attack, attacker)
    if not atk: return False
    dhp = world.get(HP, target)
    if not dhp: return False
    dmg = _calc_attack(world, attacker, atk.damage)
    dhp.current = max(0, dhp.current - dmg)
    if log:
        an = world.get(Name, attacker).text
        dn = world.get(Name, target).text
        if not an: an = "something"
        if not dn: an = "something"
        if dn == "player":
            log.add(f"{an.capitalize()} hits you for {dmg}.")
        elif an == "player":
            log.add(f"You hit {dn} for {dmg}.")
        else:
            log.add(f"{an.capitalize()} hits {dn} for {dmg}.")
    if dhp.current <= 0:
        die(world, game_map, target, log)
    return True

