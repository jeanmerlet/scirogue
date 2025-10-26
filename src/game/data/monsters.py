#from ..ecs.components import Position, Renderable, Actor

MONSTERS = {
    "skitterling": {
        "glyph": "s",
        "color": "purple",
        "hp": 4,
        "attack": 1,
        "speed": 1.5,
        "ai": "melee",
        "desc": "A small, fast scuttling alien.",
    },
    "skittermaw": {
        "glyph": "M",
        "color": "purple",
        "hp": 12,
        "attack": 4,
        "speed": 1.0,
        "ai": "melee",
        "desc": "A heavy predator with jaws like hydraulic cutters.",
    },
    "skitterseer": {
        "glyph": "s",
        "color": "purple",
        "hp": 6,
        "attack": 2,
        "speed": 1.0,
        "ai": "seer",
        "desc": "An eerie psychic Skitter that senses vibrations through metal.",
    },
}

