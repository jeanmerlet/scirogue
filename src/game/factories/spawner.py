from ..ecs.world import World
from ..ecs.components import *
from ..data.monsters import MONSTERS

def spawn_monster(world, kind, x, y):
    data = MONSTERS[kind]
    eid = world.create()
    world.add(eid, Position(x, y))
    world.add(eid, Renderable(data["glyph"], data["color"]))
    world.add(eid, Blocks())
    world.add(eid, Actor())
    world.add(eid, HP(data["hp"], data["hp"]))
    world.add(eid, Attack(data["attack"]))
    world.add(eid, Speed(data["speed"]))
    return eid

