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


def _visible_ray(game_map, x0, y0, through_x, through_y):
    """Yield a ray through a target tile to the visible-range boundary."""
    dx = through_x - x0
    dy = through_y - y0
    if dx == 0 and dy == 0:
        return
    scale = max(game_map.w, game_map.h) * 2
    far_x = x0 + dx * scale
    far_y = y0 + dy * scale
    for x, y in _line(x0, y0, far_x, far_y):
        if not game_map.in_bounds(x, y):
            return
        if not game_map.visible[x, y]:
            return
        yield x, y


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


def clear_terrain_line(game_map, x0, y0, x1, y1):
    """Return whether terrain permits a shot between two tiles."""
    return all(
        not game_map.block[x, y] and not game_map.edge[x, y]
        for x, y in _line(x0, y0, x1, y1)
    )


def _log_blocked_shot(log, attacker_name):
    if not log:
        return
    if attacker_name == "player":
        log.add("Your shot hits an obstruction.")
    else:
        log.add(f"{attacker_name.capitalize()}'s shot hits an obstruction.")


def _log_empty_shot(log, attacker_name):
    if not log:
        return
    if attacker_name == "player":
        log.add("You fire into empty space.")
    else:
        log.add(f"{attacker_name.capitalize()} fires into empty space.")


def _fire_weapon(world, game_map, attacker, weapon, target_x, target_y,
                 log, projectile_callback):
    attacker_pos = world.get(Position, attacker)
    attacker_name = world.get(Name, attacker).text or "something"
    source = (attacker_pos.x, attacker_pos.y)
    path = []
    missed_actor = False
    for x, y in _visible_ray(
            game_map, attacker_pos.x, attacker_pos.y,
            target_x, target_y):
        path.append((x, y))
        target = game_map.actors[x, y]
        if target >= 0 and target != attacker:
            defender_hp = world.get(HP, target)
            if defender_hp is None:
                if projectile_callback:
                    projectile_callback(source, path, weapon.color)
                _log_blocked_shot(log, attacker_name)
                return
            defender_name = world.get(Name, target).text or "something"
            _, _, _, hit = roll_to_hit(
                world, attacker, target, "ranged", game_map.rng, weapon
            )
            if not hit:
                _log_ranged_result(
                    log, attacker_name, defender_name, False
                )
                missed_actor = True
                continue
            if projectile_callback:
                projectile_callback(source, path, weapon.color)
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
            return

        if game_map.block[x, y] or game_map.edge[x, y]:
            if projectile_callback:
                projectile_callback(source, path, weapon.color)
            _log_blocked_shot(log, attacker_name)
            return

    if projectile_callback:
        projectile_callback(source, path, weapon.color)
    if not missed_actor:
        _log_empty_shot(log, attacker_name)


def fire_ranged(world, game_map, attacker, target_x, target_y, log=None,
                projectile_callback=None):
    """Fire a ranged group, stopping each shot at its first blocker."""
    weapons = attack_weapons(world, attacker, "ranged")
    if not weapons:
        return False

    for weapon in weapons:
        _fire_weapon(
            world, game_map, attacker, weapon, target_x, target_y, log,
            projectile_callback
        )
    return True
