from ..components import *
from .combat_calculations import (
    attack_weapons,
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

    an = world.get(Name, attacker).text or "something"
    dn = world.get(Name, target).text or "something"
    weapons = attack_weapons(world, attacker, "melee")
    if not weapons and atk is None:
        return False

    # Legacy fixed-damage actors get one fallback attack. Natural attack
    # groups resolve every listed weapon as part of the same monster action.
    attack_sequence = weapons or [None]
    for weapon in attack_sequence:
        _, _, _, hit = roll_to_hit(
            world, attacker, target, "melee", game_map.rng, weapon
        )
        if not hit:
            if log:
                if dn == "player":
                    log.add(f"{an.capitalize()} misses you.")
                elif an == "player":
                    log.add(f"You miss {dn}.")
                else:
                    log.add(f"{an.capitalize()} misses {dn}.")
            continue

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
            break
    return True
