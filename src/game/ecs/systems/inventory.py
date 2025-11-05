from ..components import *

def pick_up(world, game_map, actor_eid, item_eid, log):
    inv = world.get(Inventory, actor_eid)
    if not inv: return False
    item = world.get(Item, item_eid)
    if not item: return False
    name = world.get(Name, item_eid).text
    pos = world.get(Position, actor_eid)
    x, y = pos.x, pos.y
    if item.stackable and len(inv.items) > 0:
        inv_names = [world.get(Name, eid).text for eid in inv.items]
        inv_items = [world.get(Item, eid) for eid in inv.items]
        for i, inv_name in enumerate(inv_names):
            if name == inv_name:
                # TODO: new stack when Item.max_count is reached
                inv_items[i].count += item.count
                game_map.items[x, y].remove(item_eid)
                world.destroy(item_eid)
                log.add(f"You pick up the {name}.")
                return True
    if len(inv.items) >= inv.capacity:
        log.add("You can't carry any more.")
        return False
    game_map.items[x, y].remove(item_eid)
    world.remove(item_eid, Position)
    inv.items.append(item_eid)
    log.add(f"You pick up the {name}.")
    return True

def drop(world, game_map, actor_eid, item_eid, log):
    inv = world.get(Inventory, actor_eid)
    if not inv: return False
    item = world.get(Item, item_eid)
    if not item: return False
    pos = world.get(Position, actor_eid)
    x, y, z = pos.x, pos.y, pos.z
    if item.stackable and item.count > 1:
        # TODO: handle dropping n of a stack
        # TODO: handle stacking item on the ground
        item.count -= 1
        item_drop = world.duplicate(item_eid)
        world.add(item_drop, Position(x, y, z))
        game_map.items[x, y].insert(0, item_drop)
    else:
        inv.items.remove(item_eid)
        world.add(item_eid, Position(x, y, z))
        game_map.items[x, y].insert(0, item_eid)
    name = world.get(Name, item_eid).text
    log.add(f"You drop the {name}.")
    return True

def _occupy_two_hands(inv, equip, item_eid, name, log):
    inv.items.remove(item_eid)
    equip.slots["hand1"] = item_eid
    equip.slots["hand2"] = item_eid
    log.add(f"You equip the {name} in both hands.")

def equip_item(world, actor_eid, item_eid, log):
    inv = world.get(Inventory, actor_eid)
    equip = world.get(Equipment, actor_eid)
    if not equip:
        log.add("You cannot equip items.")
        return False
    name = world.get(Name, item_eid).text
    eq = world.get(Equippable, item_eid)
    if not eq:
        log.add(f"{name.capitalize()} is not equippable.")
        return False
    slot = eq.slot
    if slot not in equip.slots.keys():
        # TODO: a vs. no article for plural slot (e.g., feet)
        log.add(f"You're don't have a {slot}.")
        return False
    if eq.two_handed:
        if (equip.slots["hand1"] is None and equip.slots["hand2"] is None):
            _occupy_two_hands(inv, equip, item_eid, name, log)
            return True
        elif (equip.slots["hand1"] is not None and
              unequip_slot(world, actor_eid, "hand1")):
            _occupy_two_hands(inv, equip, item_eid, name, log)
            return True
        elif (equip.slots["hand2"] is not None and
              unequip_slot(world, actor_eid, "hand2")):
            _occupy_two_hands(inv, equip, item_eid, name, log)
            return True
        else:
            log.add("Need both hands free.")
            return False
    else:
        if equip.slots[slot] is None:
            inv.items.remove(item_eid)
            equip.slots[slot] = item_eid
            log.add(f"You equip the {name}.")
            return True
        else:
            #TODO: two turns taken for unequip + equip
            if unequip_slot(world, actor_eid, slot):
                inv.items.remove(item_eid)
                equip.slots[slot] = item_eid
                log.add(f"You equip the {name}.")
                return True
            else:
                return False

def _free_two_hands(equip):
    equip.slots["hand1"] = None
    equip.slots["hand2"] = None

def unequip_slot(world, actor_eid, slot):
    equip = world.get(Equipment, actor_eid)
    if not equip:
        log.add("You cannot equip items.")
        return False
    eid = equip.slots.get(slot)
    if eid is None:
        log.add("That slot is already empty.")
        return False
    eq = world.get(Equippable, eid)
    inv = world.get(Inventory, actor_eid)
    if len(inv.items) >= inv.capacity:
        #TODO: drop on ground instead with log about it
        log.add("Drop something first.")
        return False
    if eq and eq.two_handed and slot in ["hand1", "hand2"]:
        _free_two_hands(equip)
    else:
        equip.slots[slot] = None
    inv.items.append(eid)
    return True

def _consume(world, actor_eid, item_eid):
    inv = world.get(Inventory, actor_eid)
    if not inv: return
    # remove from inventory (no stacks merging here; add if needed)
    try:
        inv.items.remove(item_eid)
    except ValueError:
        pass
    # delete entity
    for table in world.components.values():
        table.pop(item_eid, None)

def use_consumable(world, actor_eid, item_eid) -> Tuple[bool,str]:
    cons = world.get(Consumable, item_eid)
    if not cons: return (False, "Not consumable.")
    eff = cons.effect_id
    # Simple demo effects:
    if eff == "stimpack":
        hp = world.get(HP, actor_eid)
        if hp:
            hp.current = min(hp.maximum, hp.current + 5)
            _consume(world, actor_eid, item_eid)
            return (True, "You inject a stimpack (+5 HP).")
        return (False, "Nothing happens.")
    elif eff == "oxygen_can":
        # you said you have an oxygen bar; stub in here
        # e.g., world.get(Oxygen, actor).current = min(max, current + 20)
        _consume(world, actor_eid, item_eid)
        return (True, "You replenish oxygen.")
    else:
        return (False, f"Unknown effect {eff!r}.")
