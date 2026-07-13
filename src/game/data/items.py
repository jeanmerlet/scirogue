import csv
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent


def _read_tsv(filename):
    with (_DATA_DIR / filename).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file, delimiter="\t"))


def _parse_bool(value):
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"Expected true or false, got {value!r}")
    return normalized == "true"


def _parse_area(value):
    value = value.strip()
    return "" if value in {"", "0"} else value


def _load_weapons():
    weapons = {}
    for row in _read_tsv("weapons.tsv"):
        name = row["weapon_base"].strip()
        if name in weapons:
            raise ValueError(f"Duplicate weapon_base: {name!r}")
        weapons[name] = {
            "kind": "weapon",
            "name": name,
            "desc": "",
            "ch": ")",
            "color": row["color"].strip(),
            "stackable": False,
            "tier": int(row["tier"]),
            "hands": int(row["hands"]),
            "damage_types": tuple(
                value.strip().lower()
                for value in row["dmg_type"].split(",")
            ),
            "skill": row["skill"].strip().lower(),
            "accuracy": int(row["accuracy"]),
            "attack_speed": int(row["atk_speed"]),
            "attack_damage": int(row["atk_dmg"]),
            "area": _parse_area(row["area"]),
            "penetration": int(row["penetration"]),
            "recoil": int(row["recoil"]),
            "noise": int(row["noise"]),
            "destructs_tiles": _parse_bool(row["destructs_tiles"]),
        }
    return weapons


def _load_armor():
    armor = {}
    for row in _read_tsv("armor.tsv"):
        name = row["armor_base"].strip()
        if name in armor:
            raise ValueError(f"Duplicate armor_base: {name!r}")
        armor[name] = {
            "kind": "armor",
            "name": name,
            "desc": "",
            "ch": "[",
            "color": row["color"].strip(),
            "stackable": False,
            "tier": int(row["tier"]),
            "slot": row["slot"].strip().lower(),
            "armor_value": int(row["armor_value"]),
            "kinetic_resistance": float(row["kinetic_res"]),
            "thermal_resistance": float(row["thermal_res"]),
            "em_resistance": float(row["em_res"]),
            "encumbrance": int(row["encumbrance"]),
            "noise": int(row["noise"]),
        }
    return armor


WEAPONS = _load_weapons()
ARMOR = _load_armor()

duplicate_names = WEAPONS.keys() & ARMOR.keys()
if duplicate_names:
    duplicates = ", ".join(sorted(duplicate_names))
    raise ValueError(f"Duplicate equipment names across catalogs: {duplicates}")

ITEMS = {**WEAPONS, **ARMOR}
ITEM_KEYS = tuple(ITEMS)
