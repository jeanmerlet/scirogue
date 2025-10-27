from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class Position:
    x: int
    y: int

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
class AI:
    pass

# --- Inventory / Equipment --- #

@dataclass
class Inventory:
    capacity: int = 26
    items: []

@dataclass
class Equipment:
    slots: {
        "hand1": None,
        "hand2": None,
        "head": None,
        "body": None,
        "legs": None,
        "feet": None
    }

@dataclass
class Slot(Enum):
    HAND1 = auto()
    HAND2 = auto()
    HEAD  = auto()
    BODY  = auto()
    LEGS  = auto()
    FEET  = auto()

@dataclass
class Item:
    name: str
    stackable: bool = False
    count: int = 1
    max_count: int = 1

@dataclass
class Consumable:
    effect_id: str

@dataclass
class Equippable:
    slots: []
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

