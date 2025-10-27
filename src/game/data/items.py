ITEMS = {
    # --- Consumables --- #
    "stimpack": {
        "kind": "consumable",
        "ch": "!",
        "color": "light red",
        "name": "Stimpack",
        "effect_id": "stimpack",
        "stackable": True,
    },
    "oxygen_can": {
        "kind": "consumable",
        "ch": "!",
        "color": "light blue",
        "name": "Oxygen Canister",
        "effect_id": "oxygen_can",
        "stackable": True,
    },
    # --- Weapons --- #
    "crowbar": {
        "kind": "equip",
        "ch": ")",
        "color": "dark red",
        "name": "Crowbar",
        "slots": ["hand1", "hand2"],
        "two_handed": False,
        "attack_bonus": 2,
    },
    "coil_rifle": {
        "kind": "equip",
        "ch": ")",
        "color": "light grey",
        "name": "Coil Rifle",
        "slots": ["hand1", "hand2"],
        "two_handed": True,
        "attack_bonus": 4,
    },
    # --- Headgear --- #
    "targeting_visor": {
        "kind": "equip",
        "ch": "[",
        "color": "cyan",
        "name": "Targeting Visor",
        "slots": ["HEAD"],
        "attack_bonus": 1,
    },
    # --- Bodygear --- #
    "stealth_suit": {
        "kind": "equip",
        "ch": "[",
        "color": "green",
        "name": "Stealth Suit",
        "slots": ["BODY"],
        "defense_bonus": 1,
        "oxy_bonus": 1,
    },
    # --- Footgear --- #
    "mag_boots": {
        "kind": "equip",
        "ch": "[",
        "color": "light grey",
        "name": "Mag Boots",
        "slots": ["FEET"],
        "defense_bonus": 1,
    },
}
