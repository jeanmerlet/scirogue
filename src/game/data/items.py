ITEMS = {
    # --- Consumables --- #
    "stimpack": {
        "kind": "consumable",
        "ch": "!",
        "color": "light red",
        "name": "stimpack",
        "effect_id": "stimpack",
        "stackable": True,
    },
    "oxygen_can": {
        "kind": "consumable",
        "ch": "!",
        "color": "light blue",
        "name": "oxygen canister",
        "effect_id": "oxygen_can",
        "stackable": True,
    },
    # --- Weapons --- #
    "crowbar": {
        "kind": "equip",
        "ch": ")",
        "color": "dark red",
        "name": "crowbar",
        "slots": ["hand1", "hand2"],
        "two_handed": False,
        "attack_bonus": 2,
    },
    "coil_rifle": {
        "kind": "equip",
        "ch": ")",
        "color": "light grey",
        "name": "coil rifle",
        "slots": ["hand1", "hand2"],
        "two_handed": True,
        "attack_bonus": 4,
    },
    # --- Headgear --- #
    "targeting_visor": {
        "kind": "equip",
        "ch": "[",
        "color": "cyan",
        "name": "targeting visor",
        "slots": ["head"],
        "attack_bonus": 1,
    },
    # --- Bodygear --- #
    "stealth_suit": {
        "kind": "equip",
        "ch": "[",
        "color": "green",
        "name": "stealth suit",
        "slots": ["body"],
        "defense_bonus": 1,
        "oxy_bonus": 1,
    },
    # --- Footgear --- #
    "mag_boots": {
        "kind": "equip",
        "ch": "[",
        "color": "light grey",
        "name": "mag boots",
        "slots": ["feet"],
        "defense_bonus": 1,
    },
}
