from dataclasses import dataclass

from ..components import Skills
from .combat_calculations import attack_weapon


STANDARD_ACTION_COST = 1000
WEAPON_SPEED_REFERENCE = 10_000
SKILL_SPEED_PER_POINT = 0.02
SKILL_SPEED_CAP = 8
TIME_QUANTUM = 10


def _round_to_quantum(value, quantum=TIME_QUANTUM):
    return max(quantum, int(value / quantum + 0.5) * quantum)


def weapon_attack_cost(attack_speed, skill_rank=0):
    if attack_speed <= 0:
        raise ValueError("Weapon attack speed must be positive.")
    capped_skill = min(SKILL_SPEED_CAP, max(0, skill_rank))
    effective_speed = attack_speed * (
        1 + capped_skill * SKILL_SPEED_PER_POINT
    )
    return _round_to_quantum(WEAPON_SPEED_REFERENCE / effective_speed)


def player_attack_cost(world, actor_eid, skill):
    weapon = attack_weapon(world, actor_eid, skill)
    if weapon is None:
        return STANDARD_ACTION_COST
    skills = world.get(Skills, actor_eid)
    skill_rank = getattr(skills, skill, 0) if skills is not None else 0
    return weapon_attack_cost(weapon.attack_speed, skill_rank)


@dataclass
class ActionClock:
    elapsed: int = 0

    def spend(self, cost):
        if cost < 0:
            raise ValueError("Action cost cannot be negative.")
        self.elapsed += cost
        npc_turns, self.elapsed = divmod(
            self.elapsed, STANDARD_ACTION_COST
        )
        return npc_turns
