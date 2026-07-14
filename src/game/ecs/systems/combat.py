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


def _line(x0, y0, x1, y1):
    """Yield Bresenham line coordinates after the origin."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    while (x0, y0) != (x1, y1):
        twice_error = 2 * error
        if twice_error >= dy:
            error += dy
            x0 += sx
        if twice_error <= dx:
            error += dx
            y0 += sy
        yield x0, y0


def _log_ranged_result(log, attacker_name, defender_name, hit, damage=0):
    if not log:
        return
    if not hit:
        if defender_name == "player":
            log.add(f"{attacker_name.capitalize()} misses you.")
        elif attacker_name == "player":
            log.add(f"You miss {defender_name}.")
        else:
            log.add(
                f"{attacker_name.capitalize()} misses {defender_name}."
            )
    elif defender_name == "player":
        log.add(f"{attacker_name.capitalize()} hits you for {damage}.")
    elif attacker_name == "player":
        log.add(f"You hit {defender_name} for {damage}.")
    else:
        log.add(
            f"{attacker_name.capitalize()} hits {defender_name} "
            f"for {damage}."
        )


def fire_ranged(world, game_map, attacker, target_x, target_y, log=None):
    """Fire at a tile, stopping at the first actor or blocking tile."""
    weapon = attack_weapons(world, attacker, "ranged")
    weapon = weapon[0] if weapon else None
    if weapon is None:
        return False

    attacker_pos = world.get(Position, attacker)
    attacker_name = world.get(Name, attacker).text or "something"
    for x, y in _line(
            attacker_pos.x, attacker_pos.y, target_x, target_y):
        target = game_map.actors[x, y]
        if target >= 0 and target != attacker:
            defender_hp = world.get(HP, target)
            if defender_hp is None:
                return True
            defender_name = world.get(Name, target).text or "something"
            _, _, _, hit = roll_to_hit(
                world, attacker, target, "ranged", game_map.rng, weapon
            )
            if not hit:
                _log_ranged_result(
                    log, attacker_name, defender_name, False
                )
                return True
            damage = calculate_damage(
                world, attacker, target, "ranged", game_map.rng,
                weapon=weapon
            )
            defender_hp.current = max(0, defender_hp.current - damage)
            _log_ranged_result(
                log, attacker_name, defender_name, True, damage
            )
            if defender_hp.current <= 0:
                die(world, game_map, target, log)
            return True

        if game_map.block[x, y] or game_map.edge[x, y]:
            if log:
                log.add("Your shot hits an obstruction.")
            return True

    if log:
        log.add("You fire into empty space.")
    return True
