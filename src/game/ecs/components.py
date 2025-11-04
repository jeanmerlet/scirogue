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
    pass

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

# --- Player --- #

@dataclass
class Oxygen:
    current: int
    maximum: int

@dataclass
class FOVRadius:
    radius: int

# --- Combat --- #

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

