from ..components import (
    AbilityScores,
    Armor,
    Attacks,
    CombatStats,
    Equipment,
    Skills,
    Weapon,
)


SKILL_ABILITIES = {
    "melee": ("vigor", "equilibrium"),
    "ranged": ("awareness", "equilibrium"),
    "mobility": ("equilibrium", "vigor"),
    "mitigation": ("vigor", "reasoning"),
}


def ability_modifier(score):
    return (score - 10) // 2


def minor_ability_modifier(score):
    return int(ability_modifier(score) / 2)


def effective_skill(world, actor_eid, skill):
    if skill not in SKILL_ABILITIES:
        raise ValueError(f"Unknown skill: {skill!r}")
    skills = world.get(Skills, actor_eid)
    abilities = world.get(AbilityScores, actor_eid)
    if skills is None or abilities is None:
        return 0
    major_name, minor_name = SKILL_ABILITIES[skill]
    return (
        getattr(skills, skill)
        + ability_modifier(getattr(abilities, major_name))
        + minor_ability_modifier(getattr(abilities, minor_name))
    )


def attack_weapon(world, actor_eid, skill):
    attacks = world.get(Attacks, actor_eid)
    if attacks is not None:
        for weapon in attacks.attacks:
            if weapon.skill == skill:
                return weapon

    equipment = world.get(Equipment, actor_eid)
    if equipment is None:
        return None
    seen = set()
    for slot in ("hand1", "hand2"):
        item_eid = equipment.slots.get(slot)
        if item_eid is None or item_eid in seen:
            continue
        seen.add(item_eid)
        weapon = world.get(Weapon, item_eid)
        if weapon is not None and weapon.skill == skill:
            return weapon
    return None


def attack_bonus(world, actor_eid, skill, weapon=None):
    skills = world.get(Skills, actor_eid)
    abilities = world.get(AbilityScores, actor_eid)
    if skills is not None and abilities is not None:
        bonus = effective_skill(world, actor_eid, skill)
    else:
        stats = world.get(CombatStats, actor_eid)
        bonus = getattr(stats, skill, 0) if stats is not None else 0
    if weapon is None:
        weapon = attack_weapon(world, actor_eid, skill)
    if weapon is not None:
        bonus += weapon.accuracy
    return bonus


def equipment_encumbrance(world, actor_eid):
    equipment = world.get(Equipment, actor_eid)
    if equipment is None:
        return 0
    total = 0
    seen = set()
    for item_eid in equipment.slots.values():
        if item_eid is None or item_eid in seen:
            continue
        seen.add(item_eid)
        armor = world.get(Armor, item_eid)
        if armor is not None:
            total += armor.encumbrance
    return total


def evasion(world, actor_eid):
    skills = world.get(Skills, actor_eid)
    abilities = world.get(AbilityScores, actor_eid)
    if skills is not None and abilities is not None:
        dodge_bonus = effective_skill(world, actor_eid, "mobility")
    else:
        stats = world.get(CombatStats, actor_eid)
        dodge_bonus = stats.dodge if stats is not None else 0
    return 10 + dodge_bonus - equipment_encumbrance(world, actor_eid)


def hit_chance(attack_bonus_value, evasion_value):
    successful_rolls = max(
        0, min(20, 20 + attack_bonus_value - evasion_value)
    )
    return successful_rolls / 20


def actor_hit_chance(world, attacker_eid, defender_eid, skill,
                     weapon=None):
    return hit_chance(
        attack_bonus(world, attacker_eid, skill, weapon),
        evasion(world, defender_eid)
    )


def roll_to_hit(world, attacker_eid, defender_eid, skill, rng,
                weapon=None):
    bonus = attack_bonus(world, attacker_eid, skill, weapon)
    defense = evasion(world, defender_eid)
    roll = rng.randint(1, 20)
    total = roll + bonus
    return roll, total, defense, total > defense
