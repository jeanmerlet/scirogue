from .ecs.systems.input import Input
from .ecs.systems.render import render_all
from .ecs.systems.inventory import drop, equip_item, unequip_slot
from .ecs.components import *
from .ui.render_menu import *
from .ui.description import render_desc
from .ui.widgets import clear_area

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

class Menu():
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        self.term = term
        self.world = world
        self.map = game_map
        self.player = player_eid
        self.log = log
        self.prev_state = prev_state
        self.prev_state.turn_taken = False
        self.sel_idx = 0
        self.hint = None

    def _lines(self):
        raise NotImplementedError

    def _render(self, lines, w):
        clear_area(self.term, 0, 0, self.map.w + 1, self.map.h + 1)
        render_all(self.term, self.world, self.map)
        render_menu(self.term, self.title, lines, w, self.sel_idx)

    def tick(self):
        cmd = self.input.poll(self.term)
        if not cmd: return self, None
        if cmd[0] == "quit":
            return self.prev_state, None
        elif cmd[0] == "up":
            self.sel_idx = max(0, self.sel_idx - 1)
            return self, None
        elif cmd[0] == "down":
            self.sel_idx = min(self.num_lines - 1, self.sel_idx + 1)
            return self, None
        return None, cmd

class EquipmentMenu(Menu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)
        self.input = Input("equip", ["menu", "cancel", "letters"])
        self.title = 'Equipment'

    def _lines(self):
        equip = self.world.get(Equipment, self.player)
        out = []
        longest_line = 0
        ljust_len = max([len(slot) for slot in equip.slots.keys()]) + 2
        for i, (slot, eid) in enumerate(equip.slots.items()):
            line_len = 0
            if eid is None:
                item_text = "(empty)"
                line_len += len(item_text)
            else:
                name = self.world.get(Name, eid).text
                color = self.world.get(Renderable, eid).color
                item_text = f"[color={color}]{name}[/color]"
                line_len += len(name) + 1
            line = f"{slot.capitalize()}:".ljust(ljust_len) + item_text
            idx = chr(i + 97)
            line = idx + ") " + line
            out.append(line)
            line_len += len(slot) + 8
            if line_len > longest_line: longest_line = line_len
        return out, longest_line

    def _parse_sel_cmd(self, cmd):
        slots = self.world.get(Equipment, self.player).slots
        idx_map = self.world.get(Equipment, self.player).idx_map
        num_slots = len(slots.keys())
        if len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122:
            sel_idx = ord(cmd[0]) - 97
            if sel_idx < num_slots:
                item = slots[idx_map[sel_idx]]
                if item is not None:
                    return DescMenu(self.term, self.world, item, self)
        elif cmd[0] == "select":
            item = slots[idx_map[self.sel_idx]]
            if item is not None:
                return DescMenu(self.term, self.world, item, self)
        return None

    def tick(self):
        lines, w = self._lines()
        self.num_lines = len(lines)
        w = max(w, len(self.title))
        super()._render(lines, w)
        state, cmd = super().tick()
        if state: return state
        if ((len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122) or
            cmd[0] == "select"):
            state = self._parse_sel_cmd(cmd)
        if state: return state
        return self

class InventoryMenu(Menu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)
        self.input = Input("inv", ["menu", "cancel", "letters"])
        self.title = 'Inventory'

    def _lines(self):
        inv = self.world.get(Inventory, self.player)
        out = []
        longest_line = 0
        for i, eid in enumerate(inv.items):
            line_len = 0
            name = self.world.get(Name, eid).text
            item = self.world.get(Item, eid)
            color = self.world.get(Renderable, eid).color
            idx = chr(i + 97)
            if item.stackable and item.count > 1:
                line = f"{item.count} [color={color}]{name}s[/color]."
                line_len += len(str(item.count)) + len(name) + 3
            else:
                line = f"A [color={color}]{name}[/color]."
                line_len += len(name) + 3
            line = idx + ") " + line
            out.append(line)
            line_len += 7
            if line_len > longest_line: longest_line = line_len
        return out, longest_line

    def _parse_sel_cmd(self, cmd):
        items = self.world.get(Inventory, self.player).items
        num_items = len(items)
        if len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122:
            sel_idx = ord(cmd[0]) - 97
            if sel_idx < num_items:
                item = items[sel_idx]
                return DescMenu(self.term, self.world, item, self)
        elif cmd[0] == "select":
            if self.sel_idx < num_items:
                item = items[self.sel_idx]
                return DescMenu(self.term, self.world, item, self)
        return None

    def tick(self):
        lines, w = self._lines()
        self.num_lines = len(lines)
        w = max(w, len(self.title) + 3)
        super()._render(lines, w)
        state, cmd = super().tick()
        if state: return state
        if ((len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122) or 
            cmd[0] == "select"):
            state = self._parse_sel_cmd(cmd)
            if state:
                return state
            else:
                return None
        return self

class DropMenu(InventoryMenu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)

    def _parse_sel_cmd(self, cmd):
        items = self.world.get(Inventory, self.player).items
        num_items = len(items)
        if len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122:
            sel_idx = ord(cmd[0]) - 97
            if sel_idx < num_items:
                item = items[sel_idx]
                if drop(self.world, self.map, self.player, item, self.log):
                    self.prev_state.turn_taken = True
                    return self.prev_state
        elif cmd[0] == "select":
            if self.sel_idx < num_items:
                item = items[self.sel_idx]
                if drop(self.world, self.map, self.player, item, self.log):
                    self.prev_state.turn_taken = True
                    return self.prev_state
        return None

class UnequipMenu(EquipmentMenu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)

    def _parse_sel_cmd(self, cmd):
        slots = list(self.world.get(Equipment, self.player).slots.keys())
        num_slots = len(slots)
        if len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122:
            sel_idx = ord(cmd[0]) - 97
            if sel_idx < num_slots:
                slot = slots[sel_idx]
                if unequip_slot(self.world, self.player, slot, self.log):
                    self.prev_state.turn_taken = True
                return self.prev_state
        elif cmd[0] == "select":
            if self.sel_idx < num_slots:
                slot = slots[self.sel_idx]
                if unequip_slot(self.world, self.player, slot, self.log):
                    self.prev_state.turn_taken = True
                return self.prev_state
        return None

class EquipMenu(InventoryMenu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)

    def _lines(self):
        inv = self.world.get(Inventory, self.player)
        out = []
        longest_line = 0
        idx = 0
        for i, eid in enumerate(inv.items):
            if not self.world.has(eid, Equippable): continue
            line_len = 0
            name = self.world.get(Name, eid).text
            item = self.world.get(Item, eid)
            color = self.world.get(Renderable, eid).color
            letter_idx = chr(idx + 97)
            if item.stackable and item.count > 1:
                line = f"{item.count} [color={color}]{name}s[/color]."
                line_len += len(str(item.count)) + len(name) + 3
            else:
                line = f"A [color={color}]{name}[/color]."
                line_len += len(name) + 3
            line = letter_idx + ") " + line
            out.append(line)
            line_len += 7
            if line_len > longest_line: longest_line = line_len
            idx += 1
        return out, longest_line

    def _parse_sel_cmd(self, cmd):
        items = self.world.get(Inventory, self.player).items
        items = [item for item in items if self.world.has(item, Equippable)]
        num_items = len(items)
        if len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122:
            sel_idx = ord(cmd[0]) - 97
            if sel_idx < num_items:
                item = items[sel_idx]
                if equip_item(self.world, self.player, item, self.log):
                    self.prev_state.turn_taken = True
                    return self.prev_state
        elif cmd[0] == "select":
            if self.sel_idx < num_items:
                if equip_item(self.world, self.player, item, self.log):
                    self.prev_state.turn_taken = True
                    return self.prev_state
        return None

class ElevatorMenu(Menu):
    def __init__(self, term, world, derelict, player_eid, elev_eid, log,
                 prev_state):
        super().__init__(term, world, player_eid, log, prev_state)
        self.input = Input("elevator", ["menu", "cancel", "numbers"])
        self.sel_idx = 0
        sid = world.get(ElevatorLanding, elev_eid).shaft_id
        self.shaft = derelict.shafts[sid]
        self.eid = elev_eid
        self.p_lvl = self.world.get(Position, self.player).z

    def _lines(self, log):
        elev = self.world.get(ElevatorLanding, self.eid)
        self.sorted_levels = sorted(elev.access)
        locked = elev.locked
        out = []
        for level in self.sorted_levels:
            tag = "[[LOCKED]]" if level in locked else ""
            if level == self.p_lvl: tag += " (here)"
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
                if tgt_level == self.p_lvl: return self.prev_state
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
