from .data.actors import ACTORS
from .data.items import ITEMS
from .ecs.components import *

def spawn_actor(world, key, x, y, z):
    data = ACTORS[key]
    eid = world.create()
    world.add(eid, Name(data["name"]))
    world.add(eid, Description(data.get("desc", "")))
    world.add(eid, Position(x, y, z))
    world.add(eid, Renderable(data["ch"], data["color"], order=3))
    world.add(eid, Blocks())
    world.add(eid, Actor())
    world.add(eid, Faction(data["faction"]))
    world.add(eid, AI())
    world.add(eid, HP(data["hp"], data["hp"]))
    world.add(eid, Attack(data["attack"]))
    world.add(eid, Speed(data["speed"]))
    return eid

def spawn_item(world, key, x, y, z):
    data = ITEMS[key]
    eid = world.create()
    world.add(eid, Name(data["name"]))
    world.add(eid, Description(data.get("desc", "")))
    world.add(eid, Position(x, y, z))
    world.add(eid, Renderable(data["ch"], data["color"], order=1))
    world.add(eid, Item(data.get("stackable", False)))
    if data["kind"] == "consumable":
        world.add(eid, Consumable(data["effect_id"]))
    if data["kind"] == "equip":
        world.add(eid, Equippable(
            slot=data["slot"],
            two_handed=data.get("two_handed", False),
            attack_bonus=data.get("attack_bonus", 0),
            defense_bonus=data.get("defense_bonus", 0),
            oxy_bonus=data.get("oxy_bonus", 0)
        ))
    return eid

def spawn_elevator(world, derelict, shaft_id, level, x, y, locked_floors=None):
    eid = world.create()
    world.add(eid, Position(x, y, level))
    world.add(eid, Renderable(">", "grey", order=2))
    coverage = set(derelict.shafts[shaft_id].landings.keys())
    world.add(eid, ElevatorLanding(derelict.name, shaft_id, coverage,
              locked=set(locked_floors or [])))
    world.add(eid, Name("elevator"))
    world.add(eid, Description("It's an elevator. Hopefully it's working."))
    return eid
