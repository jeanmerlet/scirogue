from dataclasses import dataclass

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
class FOVRadius:
    radius: int

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

# combat #

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

