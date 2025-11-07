from .ecs.systems.input import Input
from .ecs.systems.render import render_all
from .ecs.systems.inventory import drop, equip_item, unequip_slot
from .ecs.components import *
from .ui.render_menu import draw_menu
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
        self.letters = False
        self.numbers = False

    def _lines(self):
        raise NotImplementedError

    def _on_select(self, idx):
        raise NotImplementedError

    def _render(self, lines, w):
        clear_area(self.term, 0, 0, self.map.w + 1, self.map.h + 1)
        render_all(self.term, self.world, self.map)
        draw_menu(self.term, self.title, lines, w, self.sel_idx)

    def _number_to_index(self, num):
        return num

    def tick(self):
        lines, w = self._lines()
        self.num_lines = len(lines)
        w = max(w, len(self.title) + 3)
        self._render(lines, w)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if cmd[0] == "quit":
            return self.prev_state
        elif cmd[0] == "up":
            self.sel_idx = max(0, self.sel_idx - 1)
        elif cmd[0] == "down":
            self.sel_idx = min(self.num_lines - 1, self.sel_idx + 1)
        elif cmd[0] == "select":
            select = self._on_select(self.sel_idx)
            if select: return select
        elif len(cmd[0]) == 1 and 97 <= ord(cmd[0]) <= 122 and self.letters:
            select = self._on_select(ord(cmd[0]) - 97)
            if select: return select
        elif len(cmd[0]) == 1 and 48 <= ord(cmd[0]) <= 57 and self.numbers:
            idx = self._number_to_index(ord(cmd[0]) - 48)
            if idx is not None:
                select = self._on_select(idx)
                if select: return select
        return self

class InventoryMenu(Menu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)
        self.input = Input("inv", ["menu", "cancel", "letters"])
        self.title = 'Inventory'
        self.letters = True
        self.eq_only = False

    def _lines(self):
        inv = self.world.get(Inventory, self.player)
        out = []
        longest_line = 0
        i = 0
        for eid in inv.items:
            if self.eq_only and not self.world.has(eid, Equippable): continue
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
            i += 1
        return out, longest_line

    def _on_select(self, idx):
        items = self.world.get(Inventory, self.player).items
        num_items = len(items)
        if idx < num_items:
            item = items[idx]
            return DescMenu(self.term, self.world, item, self)
        return False

class DropMenu(InventoryMenu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)

    def _on_select(self, idx):
        items = self.world.get(Inventory, self.player).items
        num_items = len(items)
        if idx < num_items:
            item = items[idx]
            if drop(self.world, self.map, self.player, item, self.log):
                self.prev_state.turn_taken = True
                return self.prev_state
        return False

class EquipMenu(InventoryMenu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)
        self.eq_only = True

    def _on_select(self, idx):
        items = self.world.get(Inventory, self.player).items
        items = [item for item in items if self.world.has(item, Equippable)]
        num_items = len(items)
        if idx < num_items:
            item = items[idx]
            if equip_item(self.world, self.player, item, self.log):
                self.prev_state.turn_taken = True
                return self.prev_state
        return False

class ElevatorMenu(Menu):
    def __init__(self, term, world, game_map, derelict, player_eid, elev_eid,
                 log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)
        self.input = Input("elevator", ["menu", "cancel", "numbers"])
        self.title = "Elevator"
        sid = world.get(ElevatorLanding, elev_eid).shaft_id
        self.shaft = derelict.shafts[sid]
        self.eid = elev_eid
        self.p_lvl = self.world.get(Position, self.player).z
        self.numbers = True

    def _lines(self):
        elev = self.world.get(ElevatorLanding, self.eid)
        self.sorted_levels = sorted(elev.access)
        locked = elev.locked
        out = []
        longest_line = 0
        for level in self.sorted_levels:
            line_len = 0
            tag = "[[LOCKED]]" if level in locked else ""
            if level == self.p_lvl: tag += " (here)"
            line = f"[[{level}]] {tag}".strip()
            out.append(line)
            line_len += len(line) + 5
            if line_len > longest_line: longest_line = line_len
        return out, longest_line

    def _number_to_index(self, num):
        if num in self.sorted_levels:
            return self.sorted_levels.index(num)
        return None

    def _on_select(self, idx):
        tgt_level = self.sorted_levels[idx]
        if tgt_level in self.sorted_levels:
            if tgt_level == self.p_lvl:
                return self.prev_state
            tgt_x, tgt_y = self.shaft.landings[tgt_level]
            self.prev_state.change_level(tgt_level, tgt_x, tgt_y)
            return self.prev_state
        return False

class EquipmentMenu(Menu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)
        self.input = Input("equip", ["menu", "cancel", "letters"])
        self.title = 'Equipment'
        self.letters = True

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

    def _on_select(self, idx):
        slots = self.world.get(Equipment, self.player).slots
        idx_map = self.world.get(Equipment, self.player).idx_map
        num_slots = len(slots.keys())
        if idx < num_slots:
            item = slots[idx_map[idx]]
            if item is not None:
                return DescMenu(self.term, self.world, item, self)
        return False

class UnequipMenu(EquipmentMenu):
    def __init__(self, term, world, game_map, player_eid, log, prev_state):
        super().__init__(term, world, game_map, player_eid, log, prev_state)

    def _on_select(self, idx):
        slots = self.world.get(Equipment, self.player).slots
        idx_map = self.world.get(Equipment, self.player).idx_map
        num_slots = len(slots.keys())
        if idx < num_slots:
            slot = idx_map[idx]
            if unequip_slot(self.world, self.player, slot, self.log):
                self.prev_state.turn_taken = True
            return self.prev_state
        return False
