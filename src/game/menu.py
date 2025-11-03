from .ecs.systems.input import Input
from .ecs.components import Inventory, Item, Name, Renderable
from .ui.inventory import render_inventory
from .ui.inspect import render_desc

class DescMenu():
    def __init__(self, term, world, ent_eid, prev_state):
        self.term = term
        self.input = Input("desc")
        self.world = world
        self.eid = ent_eid
        self.prev_state = prev_state

    def tick(self):
        render_desc(self.term, self.world, self.eid)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if cmd[0] == "quit": return self.prev_state
        return self

class InventoryMenu():
    def __init__(self, term, world, player_eid, log, prev_state):
        self.term = term
        self.input = Input("inventory")
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
        render_inventory(self.term, lines, self.sel_idx)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if len(cmd) == 1 and 97 <= ord(cmd) <= 122:
            sel_idx = ord(cmd) - 97
            num_items = len(self.world.get(Inventory, self.player).items)
            if sel_idx < num_items:
                item = self.world.get(Inventory, self.player).items[sel_idx]
                return DescMenu(self.term, self.world, item, self)
        elif cmd == "select":
            item = self.world.get(Inventory, self.player).items[self.sel_idx]
            return DescMenu(self.term, self.world, item, self)
        elif cmd == "up":
            self.sel_idx = max(0, self.sel_idx - 1)
        elif cmd == "down":
            self.sel_idx = min(len(lines) - 1, self.sel_idx + 1)
        elif cmd == "quit":
            return self.prev_state
        return self
