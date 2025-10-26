from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Renderable:
    ch: str
    color: str

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
class HP:
    current: int
    maximum: int

@dataclass
class Attack:
    damage: int

@dataclass
class Speed:
    mult: float

