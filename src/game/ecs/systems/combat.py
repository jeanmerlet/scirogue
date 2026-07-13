from ..components import *
from .combat_calculations import (
    attack_weapon,
    calculate_damage,
    roll_to_hit,
)

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
    dhp = world.get(HP, target)
    if not dhp: return False

    weapon = attack_weapon(world, attacker, "melee")
    _, _, _, hit = roll_to_hit(
        world, attacker, target, "melee", game_map.rng, weapon
    )
    an = world.get(Name, attacker).text or "something"
    dn = world.get(Name, target).text or "something"
    if not hit:
        if log:
            if dn == "player":
                log.add(f"{an.capitalize()} misses you.")
            elif an == "player":
                log.add(f"You miss {dn}.")
            else:
                log.add(f"{an.capitalize()} misses {dn}.")
        return True

    if weapon is None and atk is None:
        return False
    fallback_damage = atk.damage if atk is not None else 0
    dmg = calculate_damage(
        world,
        attacker,
        target,
        "melee",
        game_map.rng,
        weapon=weapon,
        fallback_damage=fallback_damage
    )
    dhp.current = max(0, dhp.current - dmg)
    if log:
        if dn == "player":
            log.add(f"{an.capitalize()} hits you for {dmg}.")
        elif an == "player":
            log.add(f"You hit {dn} for {dmg}.")
        else:
            log.add(f"{an.capitalize()} hits {dn} for {dmg}.")
    if dhp.current <= 0:
        die(world, game_map, target, log)
    return True

