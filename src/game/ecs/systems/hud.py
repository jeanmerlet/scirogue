from dataclasses import dataclass
from ..components import HP, Oxygen

@dataclass
class PlayerStats:
    hp: int; max_hp: int
    oxy: int; max_oxy: int

def get_player_stats(world, player_eid):
    hp = world.get(HP, player_eid)
    oxy = world.get(Oxygen, player_eid)
    stats = PlayerStats(
                hp      = hp.current,
                max_hp  = hp.maximum,
                oxy     = oxy.current,
                max_oxy = oxy.maximum,
            )
    return stats
