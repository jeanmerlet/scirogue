from .data.actors import ACTORS
from .data.items import ITEMS, WEAPONS
from .ecs.components import *

def _weapon_from_data(data):
    return Weapon(
        name=data["name"],
        tier=data["tier"],
        hands=data["hands"],
        damage_types=data["damage_types"],
        skill=data["skill"],
        accuracy=data["accuracy"],
        attack_speed=data["attack_speed"],
        attack_damage=data["attack_damage"],
        area=data["area"],
        penetration=data["penetration"],
        recoil=data["recoil"],
        noise=data["noise"],
        destructs_tiles=data["destructs_tiles"]
    )

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
    world.add(eid, CombatStats(
        melee=data["melee"],
        ranged=data["ranged"],
        mobility=data["mobility"],
        mitigation=data["mitigation"],
        armor_value=data["armor_value"],
        kinetic_resistance=data["kinetic_resistance"],
        thermal_resistance=data["thermal_resistance"],
        em_resistance=data["em_resistance"]
    ))
    world.add(eid, Attacks([
        _weapon_from_data(WEAPONS[attack_name])
        for attack_name in data["attacks"]
    ]))
    # Keep fixed damage working until combat.py uses CombatStats/Attacks.
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

    if data["kind"] == "weapon":
        world.add(eid, Equippable(
            slot="hand1",
            two_handed=data["hands"] == 2
        ))
        world.add(eid, _weapon_from_data(data))
    elif data["kind"] == "armor":
        world.add(eid, Equippable(slot=data["slot"]))
        world.add(eid, Armor(
            tier=data["tier"],
            armor_value=data["armor_value"],
            kinetic_resistance=data["kinetic_resistance"],
            thermal_resistance=data["thermal_resistance"],
            em_resistance=data["em_resistance"],
            encumbrance=data["encumbrance"],
            noise=data["noise"]
        ))
    elif data["kind"] == "consumable":
        world.add(eid, Consumable(data["effect_id"]))

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
