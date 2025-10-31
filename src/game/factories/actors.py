from ..ecs.world import World
from ..ecs.components import *
from ..data.actors import ACTORS

def spawn_actor(world, key, x, y):
    data = ACTORS[key]
    eid = world.create()
    world.add(eid, Name(data["name"]))
    world.add(eid, Description(data.get("desc", "")))
    world.add(eid, Position(x, y))
    world.add(eid, Renderable(data["ch"], data["color"], order=3))
    world.add(eid, Blocks())
    world.add(eid, Actor())
    world.add(eid, Faction(data["faction"]))
    world.add(eid, AI())
    world.add(eid, HP(data["hp"], data["hp"]))
    world.add(eid, Attack(data["attack"]))
    world.add(eid, Speed(data["speed"]))
    return eid

