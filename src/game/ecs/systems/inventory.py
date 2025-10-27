from ..components import *

def stack_item(world):
    pass

def pick_up(world, actor_eid, item_eid, log=None):
    inv = world.get(Inventory, actor_eid)
    if not inv: return False
    item = world.get(Item, item_eid)
    if not item: return False
    if item.stackable:
        inv_items = [world.get(Item, eid) for eid in inv.items]
        for inv_item in inv_items:
            if item.name == inv_item.name:
                inv_item.count += 1
                world.destroy(item_eid)
                log.add(f"You add the {item.name} to your stack.")
                return True
    if len(inv.items) >= inv.capacity:
        log.add("You can't carry any more.")
        return False
    world.remove(item_eid, Position)
    inv.items.append(item_eid)
    log.add(f"You pick up the {item.name}.")
    return True

def drop(world, actor_eid, item_eid, x, y):
    # TODO: handle dropping n of a stack
    inv = world.get(Inventory, actor_eid)
    if not inv: return False
    item = world.get(Item, item_eid)
    if not item: return False
    if item.count > 1 and item.stackable:
        item.count -= 1
        item_drop = world.create()
        item_drop = world.duplicate(item_eid, item_drop)
        world.add(item_drop, Position(x, y))
    else:
        inv.items.remove(item_eid)
        world.add(item_eid, Position(x, y))
    return True

def _occupy_two_hands(equipment, primary, item_eid):
    equipment.slots[primary] = item_eid
    other = "hand2" if primary == "hand1" else "hand1"
    equipment.slots[other] = item_eid

def _free_two_hands(equipment):
    equipment.slots["hand1"] = None
    equipment.slots["hand2"] = None

def equip_item(world, actor_eid, item_eid, preferred_slot, log=None):
    equipment = world.get(Equipment, actor_eid)
    if not equipment:
        log.add("No valid equipment slots.")
        return False
    eq = world.get(Equippable, item_eid)
    if not eq:
        log.add("Item is not equippable.")
        return False
    # pick target slot
    targets = eq.slots if preferred_slot is None else [preferred_slot]
    for slot in targets:
        if slot not in (Slot.HAND1, Slot.HAND2, Slot.HEAD, Slot.BODY, Slot.LEGS, Slot.FEET):
            continue
        # two-handed logic
        if eq.two_handed and slot in (Slot.HAND1, Slot.HAND2):
            # need both hands free or holding the same item (re-equip)
            if (equip.slots[Slot.HAND1] is None and equip.slots[Slot.HAND2] is None) or \
               (equip.slots[Slot.HAND1] == item_eid and equip.slots[Slot.HAND2] == item_eid):
                _occupy_two_hands(equip, item_eid, slot)
                return (True, "Equipped (2h).")
            else:
                return (False, "Both hands must be free.")
        else:
            # normal: slot must be free
            if equip.slots[slot] is None:
                equip.slots[slot] = item_eid
                return (True, "Equipped.")
    return (False, "No valid slot free.")

def unequip_slot(world, actor_eid, slot: Slot) -> Optional[int]:
    equip = world.get(Equipment, actor_eid)
    if not equip: return None
    eid = equip.slots.get(slot)
    if eid is None: return None
    eq = world.get(Equippable, eid)
    if eq and eq.two_handed and slot in (Slot.HAND1, Slot.HAND2):
        _free_two_hands(equip)
    else:
        equip.slots[slot] = None
    return eid

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

