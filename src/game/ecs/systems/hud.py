from dataclasses import dataclass
from ..components import (
    AbilityScores, Equipment, Experience, HP, Name, Oxygen, Weapon
)
from .combat_calculations import equipment_armor_value, evasion

@dataclass
class EquippedItemDisplay:
    name: str
    color: str = "light grey"

@dataclass
class PlayerDisplayData:
    hp: int; max_hp: int
    oxy: int; max_oxy: int
    awareness: int; equilibrium: int
    reasoning: int; vigor: int
    armor: int; evasion: int
    xp_level: int; xp_percent: int
    main_hand: EquippedItemDisplay
    offhand: EquippedItemDisplay

def _equipped_hand_data(world, player_eid):
    equipment = world.get(Equipment, player_eid)
    if equipment is None:
        empty = EquippedItemDisplay("Empty")
        return empty, empty

    main_eid = equipment.slots["hand1"]
    offhand_eid = equipment.slots["hand2"]

    def item_display(item_eid):
        if item_eid is None:
            return EquippedItemDisplay("Empty")
        name = world.get(Name, item_eid)
        weapon = world.get(Weapon, item_eid)
        return EquippedItemDisplay(
            name.text if name is not None else "Unknown",
            weapon.color if weapon is not None else "light grey",
        )

    main_hand = item_display(main_eid)
    if offhand_eid is not None and offhand_eid == main_eid:
        offhand = EquippedItemDisplay("Two-handed")
    else:
        offhand = item_display(offhand_eid)
    return main_hand, offhand

def get_player_stats(world, player_eid):
    hp = world.get(HP, player_eid)
    oxy = world.get(Oxygen, player_eid)
    abilities = world.get(AbilityScores, player_eid)
    experience = world.get(Experience, player_eid)
    main_hand, offhand = _equipped_hand_data(world, player_eid)
    xp_level = experience.level if experience is not None else 1
    xp_percent = 0
    if experience is not None and experience.next_level > 0:
        xp_percent = round(
            100 * experience.current / experience.next_level
        )
        xp_percent = max(0, min(100, xp_percent))
    stats = PlayerDisplayData(
                hp      = hp.current,
                max_hp  = hp.maximum,
                oxy     = oxy.current,
                max_oxy = oxy.maximum,
                awareness   = abilities.awareness,
                equilibrium = abilities.equilibrium,
                reasoning   = abilities.reasoning,
                vigor       = abilities.vigor,
                armor       = equipment_armor_value(world, player_eid),
                evasion     = evasion(world, player_eid, "ranged"),
                xp_level    = xp_level,
                xp_percent  = xp_percent,
                main_hand   = main_hand,
                offhand     = offhand,
            )
    return stats
