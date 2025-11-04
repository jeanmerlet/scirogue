from .ecs.systems.input import Input
from .ecs.components import *
from .ui.render_menu import *
from .ui.description import render_desc

class DescMenu():
    def __init__(self, term, world, ent_eid, prev_state):
        self.term = term
        self.input = Input("description", ["cancel"])
        self.world = world
        self.eid = ent_eid
        self.prev_state = prev_state

    def tick(self):
        render_desc(self.term, self.world, self.eid)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if cmd[0] == "quit": return self.prev_state
        return self

class EquipmentMenu():
    def __init__(self, term, world, player_eid, log, prev_state):
        self.term = term
        self.input = Input("equip", ["menu", "cancel"])
        self.world = world
        self.player = player_eid
        self.log = log
        self.prev_state = prev_state
        self.prev_state.turn_taken = False
        self.sel_idx = 0

    def _lines(self):
        equip = self.world.get(Equipment, self.player)
        out = []
        for i, (slot, eid) in enumerate(equip.slots.items()):
            if eid is None:
                item_text = "(empty)"
            else:
                name = self.world.get(Name, eid).text
                color = self.world.get(Renderable, eid).color
                item_text = "[color={color}]{name}s[/color]"
            line = f"{slot.capitalize()}: {item_text}"
            idx = chr(i + 97)
            line = idx + ") " + line
            out.append(line)
        return out

    def tick(self):
        lines = self._lines()
        if not lines: return self.prev_state
        render_equip_menu(self.term, lines, self.sel_idx)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if cmd[0] == "quit": return self.prev_state
        if len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122:
            sel_idx = ord(cmd[0]) - 97
            num_items = len(self.world.get(Inventory, self.player).items)
            if sel_idx < num_items:
                item = self.world.get(Equipment, self.player).slots[sel_idx]
                return DescMenu(self.term, self.world, item, self)
        elif cmd[0] == "select":
            item = self.world.get(Inventory, self.player).items[self.sel_idx]
            return DescMenu(self.term, self.world, item, self)
        elif cmd[0] == "up":
            self.sel_idx = max(0, self.sel_idx - 1)
        elif cmd[0] == "down":
            self.sel_idx = min(len(lines) - 1, self.sel_idx + 1)
        elif cmd[0] == "quit": return self.prev_state
        return self

class InventoryMenu():
    def __init__(self, term, world, player_eid, log, prev_state):
        self.term = term
        self.input = Input("inv", ["menu", "cancel"])
        self.world = world
        self.player = player_eid
        self.log = log
        self.prev_state = prev_state
        self.prev_state.turn_taken = False
        self.sel_idx = 0

    def _lines(self, log):
        inv = self.world.get(Inventory, self.player)
        if not inv:
            log.add("You don't have an inventory!")
            return False
        if not inv.items:
            log.add("Your inventory is empty.")
            return False
        out = []
        for i, eid in enumerate(inv.items):
            name = self.world.get(Name, eid).text
            item = self.world.get(Item, eid)
            color = self.world.get(Renderable, eid).color
            idx = chr(i + 97)
            if item.stackable and item.count > 1:
                line = f"{item.count} [color={color}]{name}s[/color]."
            else:
                line = f"A [color={color}]{name}[/color]."
            line = idx + ") " + line
            out.append(line)
        return out

    def tick(self):
        lines = self._lines(self.log)
        if not lines: return self.prev_state
        render_inv_menu(self.term, lines, self.sel_idx)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122:
            sel_idx = ord(cmd[0]) - 97
            num_items = len(self.world.get(Inventory, self.player).items)
            if sel_idx < num_items:
                item = self.world.get(Inventory, self.player).items[sel_idx]
                return DescMenu(self.term, self.world, item, self)
        elif cmd[0] == "select":
            item = self.world.get(Inventory, self.player).items[self.sel_idx]
            return DescMenu(self.term, self.world, item, self)
        elif cmd[0] == "up":
            self.sel_idx = max(0, self.sel_idx - 1)
        elif cmd[0] == "down":
            self.sel_idx = min(len(lines) - 1, self.sel_idx + 1)
        elif cmd[0] == "quit": return self.prev_state
        return self

class ElevatorMenu():
    def __init__(self, term, world, derelict, player_eid, elev_eid, log,
                 prev_state):
        self.term = term
        self.input = Input("elevator", ["menu", "cancel"])
        self.world = world
        sid = world.get(ElevatorLanding, elev_eid).shaft_id
        self.shaft = derelict.shafts[sid]
        self.player = player_eid
        self.eid = elev_eid
        self.log = log
        self.prev_state = prev_state
        self.prev_state.turn_taken = False
        self.sel_idx = 0

    def _lines(self, log):
        p_lvl = self.world.get(Position, self.player).z
        elev = self.world.get(ElevatorLanding, self.eid)
        self.sorted_levels = sorted(elev.access)
        locked = elev.locked
        out = []
        for level in self.sorted_levels:
            tag = "[[LOCKED]]" if level in locked else ""
            if level == p_lvl: tag += " (here)"
            out.append(f"[[{level}]] {tag}".strip())
        return out

    def tick(self):
        lines = self._lines(self.log)
        if not lines: return self.prev_state
        render_elevator_menu(self.term, lines, self.sel_idx)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if len(cmd[0]) == 1 and 48 <= ord(cmd[0]) <= 57:
            tgt_level = ord(cmd[0]) - 48
            if tgt_level in self.sorted_levels:
                tgt_x, tgt_y = self.shaft.landings[tgt_level]
                self.prev_state.change_level(tgt_level, tgt_x, tgt_y)
                return self.prev_state
        elif cmd[0] == "select":
            tgt_level = self.sorted_levels[self.sel_idx]
            tgt_x, tgt_y = self.shaft.landings[tgt_level]
            self.prev_state.change_level(tgt_level, tgt_x, tgt_y)
            return self.prev_state
        elif cmd[0] == "up":
            self.sel_idx = max(0, self.sel_idx - 1)
        elif cmd[0] == "down":
            self.sel_idx = min(len(lines) - 1, self.sel_idx + 1)
        elif cmd[0] == "quit":
            return self.prev_state
        return self
