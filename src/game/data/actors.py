import csv
from pathlib import Path


_DATA_PATH = Path(__file__).resolve().parent / "actors.tsv"


def _parse_bool(value):
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"Expected true or false, got {value!r}")
    return normalized == "true"


def _parse_attacks(value):
    return [name.strip() for name in value.split("|") if name.strip()]


def _load_actors():
    actors = {}
    with _DATA_PATH.open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file, delimiter="\t")
        for row in rows:
            key = row["actor_base"].strip()
            if key in actors:
                raise ValueError(f"Duplicate actor_base: {key!r}")

            attack_groups = {}
            melee_attacks = _parse_attacks(row["melee_attacks"])
            ranged_attacks = _parse_attacks(row["ranged_attacks"])
            if melee_attacks:
                attack_groups["melee"] = melee_attacks
            if ranged_attacks:
                attack_groups["ranged"] = ranged_attacks

            actors[key] = {
                "name": row["name"].strip(),
                "faction": row["faction"].strip().lower(),
                "role": row["role"].strip().lower(),
                "ch": row["ch"],
                "color": row["color"].strip(),
                "desc": row["desc"].strip(),
                "hp": int(row["hp"]),
                "speed": float(row["speed"]),
                "ai_type": row["ai_type"].strip().lower(),
                "flying": _parse_bool(row["flying"]),
                "melee": int(row["melee"]),
                "ranged": int(row["ranged"]),
                "dodge": int(row["dodge"]),
                "mitigation": int(row["mitigation"]),
                "armor_value": int(row["armor_value"]),
                "kinetic_resistance": float(row["kinetic_res"]),
                "thermal_resistance": float(row["thermal_res"]),
                "em_resistance": float(row["em_res"]),
                "attack_groups": attack_groups,
                "spawns_actor": row["spawns_actor"].strip(),
                "spawns_group": row["spawns_group"].strip(),
            }
    return actors


ACTORS = _load_actors()
ACTOR_KEYS = tuple(ACTORS)
