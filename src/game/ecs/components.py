from dataclasses import dataclass, field

@dataclass
class ElevatorShaft:
    shaft_id: int
    landings: dict = field(default_factory=dict) # level: (x, y)

@dataclass
class ElevatorLanding:
    ship_name: str
    shaft_id: int
    access: set = field(default_factory=set) # levels
    locked: set = field(default_factory=set) # levels
    requires_power: bool = True

@dataclass
class Keycard:
    tags: set = field(default_factory=set)

@dataclass
class PowerGrid:
    ship_id: int
    powered: bool = True

@dataclass
class Position:
    x: int
    y: int
    z: int

@dataclass
class Renderable:
    ch: str
    color: str = "white"
    order: int = 0

@dataclass
class Blocks:
    pass

@dataclass
class Opaque:
    pass

@dataclass
class Actor:
    pass

@dataclass
class Faction:
    tag: str

@dataclass
class Name:
    text: str

@dataclass
class Description:
    text: str

@dataclass
class AI:
    kind: str = "standard"

@dataclass
class Flying:
    pass

@dataclass
class Spawner:
    actor_key: str = ""
    spawn_group: str = ""

# --- Inventory / Equipment --- #

@dataclass
class Inventory:
    items: list = field(default_factory=list)
    capacity: int = 26

@dataclass
class Equipment:
    slots: dict = field(default_factory=lambda: {
        "hand1": None,
        "hand2": None,
        "head": None,
        "body": None,
        "legs": None,
        "feet": None
    })
    idx_map: dict = field(default_factory=lambda: {
        0: "hand1",
        1: "hand2",
        2: "head",
        3: "body",
        4: "legs",
        5: "feet"
    })

@dataclass
class Item:
    stackable: bool = False
    count: int = 1
    max_count: int = 1

@dataclass
class Consumable:
    effect_id: str

@dataclass
class Equippable:
    slot: str
    two_handed: bool = False
    attack_bonus: int = 0
    defense_bonus: int = 0
    oxy_bonus: int = 0

@dataclass
class Weapon:
    name: str
    tier: int
    hands: int
    damage_types: tuple
    skill: str
    accuracy: int
    attack_speed: int
    attack_damage: int
    color: str = "white"
    area: str = ""
    penetration: int = 0
    recoil: int = 0
    noise: int = 0
    destructs_tiles: bool = False

@dataclass
class Armor:
    tier: int
    armor_value: int
    kinetic_resistance: float = 0.0
    thermal_resistance: float = 0.0
    em_resistance: float = 0.0
    encumbrance: int = 0
    noise: int = 0

# --- Player --- #

@dataclass
class AbilityScores:
    awareness: int = 10
    equilibrium: int = 10
    reasoning: int = 10
    vigor: int = 10

@dataclass
class Skills:
    melee: int = 0
    ranged: int = 0
    mobility: int = 0
    mitigation: int = 0
    tech: int = 0
    stealth: int = 0
    cybernetics: int = 0
    perception: int = 0

@dataclass
class Oxygen:
    current: int
    maximum: int

@dataclass
class Experience:
    level: int = 1
    current: int = 0
    next_level: int = 100

@dataclass
class FOVRadius:
    radius: int

# --- Combat --- #

@dataclass
class CombatStats:
    melee: int = 0
    ranged: int = 0
    dodge: int = 0
    mitigation: int = 0
    armor_value: int = 0
    kinetic_resistance: float = 0.0
    thermal_resistance: float = 0.0
    em_resistance: float = 0.0

@dataclass
class Attacks:
    groups: dict = field(default_factory=dict)

@dataclass
class HP:
    current: int
    maximum: int

@dataclass
class Attack:
    damage: int

@dataclass
class Speed:
    mult: float
