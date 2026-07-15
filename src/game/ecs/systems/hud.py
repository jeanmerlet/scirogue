from dataclasses import dataclass
from ..components import AbilityScores, Experience, HP, Oxygen
from .combat_calculations import equipment_armor_value, evasion

@dataclass
class PlayerStats:
    hp: int; max_hp: int
    oxy: int; max_oxy: int
    awareness: int; equilibrium: int
    reasoning: int; vigor: int
    armor: int; evasion: int
    xp_level: int; xp_percent: int

def get_player_stats(world, player_eid):
    hp = world.get(HP, player_eid)
    oxy = world.get(Oxygen, player_eid)
    abilities = world.get(AbilityScores, player_eid)
    experience = world.get(Experience, player_eid)
    xp_level = experience.level if experience is not None else 1
    xp_percent = 0
    if experience is not None and experience.next_level > 0:
        xp_percent = round(
            100 * experience.current / experience.next_level
        )
        xp_percent = max(0, min(100, xp_percent))
    stats = PlayerStats(
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
            )
    return stats
