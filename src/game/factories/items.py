from ..ecs.world import World
from ..ecs.components import *
from ..data.items import ITEMS

def spawn_item(world, item_key, x, y):
    data = ITEMS[item_key]
    eid = world.create()
    world.add(eid, Name(data["name"]))
    world.add(eid, Position(x, y))
    world.add(eid, Renderable(data["ch"], data["color"], order=1))
    world.add(eid, Item(data["name"], data["stackable"]))
    if data["kind"] == "consumable":
        world.add(eid, Consumable(data["effect_id"]))
    if data["kind"] == "equip":
        world.add(eid, Equippable(
            slots=data["slots"],
            two_handed=data.get("two_handed", False),
            attack_bonus=data.get("attack_bonus", 0),
            defense_bonus=data.get("defense_bonus", 0),
            oxy_bonus=data.get("oxy_bonus", 0)
        ))
    return eid

