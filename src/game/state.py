from .ecs.systems.input import Input
from .ecs.systems import render as sys_render
from .ecs.systems import movement as sys_move
from .ecs.systems.ai import take_monster_turns
from .ecs.systems.inventory import pick_up, drop, equip_item, unequip_slot, use_consumable
from .ecs.world import World
from .ecs.components import *
from .map.tiles import Map
from .ecs.systems.fov import do_fov
from .factories.actors import spawn_actor
from .factories.items import spawn_item
from .ui.layout import make_layout
from .ui.panels import SidebarPanel, LogPanel
from .ui.inventory import render_inventory
from .ecs.systems.hud import get_player_stats
from .services.log import MessageLog
from random import choice, randint

class BaseState:
    def __init__(self, term):
        self.term = term

    def tick(self):
        raise NotImplementedError

class TitleState(BaseState):
    def tick(self):
        self.term.clear()
        self.term.refresh()
        return PlayState(self.term)

class PlayState(BaseState):
    def __init__(self, term):
        super().__init__(term)
        self.input = Input("play")
        self.map = Map(80, 52)
        self.map.generate_bsp(seed=102, reflect="h")
        self.world = World()
        player = self.world.create()
        startx, starty = self.map.px, self.map.py
        self.world.add(player, Position(startx, starty))
        self.map.actors[startx, starty] = player
        self.world.add(player, Name("player"))
        self.world.add(player, FOVRadius(10))
        self.world.add(player, Renderable("@", "amber", 3))
        self.world.add(player, Blocks())
        self.world.add(player, Actor())
        self.world.add(player, Inventory(capacity=26))
        self.world.add(player, Equipment())
        self.world.add(player, Faction("player"))
        self.world.add(player, HP(100, 100))
        self.world.add(player, Oxygen(100, 100))
        self.world.add(player, Attack(5))
        self.world.add(player, Speed(1.0))
        self.player = player
        self.turn_taken = False
        self.log = MessageLog()
        self.sidebar = SidebarPanel()
        self.logpanel = LogPanel()
        sidebar_w = term.w - self.map.w
        log_h = term.h - self.map.h
        self.layout = make_layout(self.term, self.map.w, self.map.h,
                                  sidebar_w, log_h)
        self._populate_map()
        self._render()

    def _populate_map(self):
        # TODO: stack items when duplicating in same spot (or increase count)
        pos = self.world.get(Position, self.player)
        for r in self.map.rooms:
            num = min(r.size(), randint(0, 2))
            for _ in range(num):
                x, y = choice(list(r.inside()))
                kind = choice(["stimpack", "crowbar",
                               "coil_rifle"])
                eid = spawn_item(self.world, kind, x, y)
                self.map.items[(x, y)].append(eid)
            if r.is_inside(pos.x, pos.y): continue
            num = min(r.size(), randint(0, 3))
            for _ in range(num):
                x, y = choice(list(r.inside()))
                if not self.map.blocked(x, y):
                    kind = choice(["skitterling", "skittermaw",
                                   "skitterseer"])
                    eid = spawn_actor(self.world, kind, x, y)
                    self.map.actors[x, y] = eid

    def _fov(self):
        pos = self.world.get(Position, self.player)
        radius = self.world.get(FOVRadius, self.player).radius
        do_fov(pos.x, pos.y, radius, self.map)

    def _render(self):
        self.term.clear()
        self._fov()
        sys_render.draw(self.term, self.world, self.map.draw, 
                        self.map.visible)
        stats = get_player_stats(self.world, self.player)
        self.sidebar.render(self.term, self.layout.sidebar, stats)
        self.logpanel.render(self.term, self.layout.log, self.log)
        self.term.refresh()

    def _handle_player_intent(self, intent):
        match intent[0]:
            case "move":
                _, dx, dy = intent
                return sys_move.try_move(self.world, self.player,
                                         dx, dy, self.map, self.log)
            case "pick_up":
                pos = self.world.get(Position, self.player)
                items_xy = self.map.items[(pos.x, pos.y)]
                num_items = len(items_xy)
                if num_items == 0:
                    return False
                elif num_items == 1:
                    item = items_xy[0]
                    return pick_up(self.world, self.player, item, self.log)
                else:
                    # pick up menu needed if more than one item
                    item = items_xy[0]
                    return pick_up(self.world, self.player, item, self.log)
            case "drop":
                # drop menu needed
                return False
            case "open_inv":
                menu = InventoryMenu(self.term, self.world, self.player,
                                     self.log, self)
                return ("switch", menu)
            case "open_menu":
                # nothing for now
                return False
            case "quit":
                return ("switch", None)
        return self

    def tick(self):
        self._render()
        intent = self.input.poll(self.term)
        outcome = self._handle_player_intent(intent)
        if isinstance(outcome, tuple) and outcome[0] == "switch":
            return outcome[1]
        if outcome or self.turn_taken:
            take_monster_turns(self.world, self.map, self.player, self.log)
        return self

class MenuState(BaseState):
    def __init__(self, term):
        super().__init__(term)
        self.input = Input("menu")

    def tick(self):
       pass 

class InventoryMenu(BaseState):
    def __init__(self, term, world, player_eid, log, prev_state):
        super().__init__(term)
        self.input = Input("inventory")
        self.world = world
        self.player = player_eid
        self.log = log
        self.prev_state = prev_state
        self.prev_state.turn_taken = False
        self.sel = 0

    def _lines(self, log):
        inv = self.world.get(Inventory, self.player)
        if not inv:
            log.add("You don't have an inventory!")
            return self.prev_state
        if not inv.items:
            log.add("Your inventory is empty.")
            return self.prev_state
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
        render_inventory(self.term, lines, self.sel)
        intent = self.input.poll(self.term)[0]
        match intent:
            case "enter" or ()
            case "up":
                self.sel = max(0, self.sel - 1)
            case "down":
                self.sel = min(len(lines) - 1, self.sel + 1)
            case "quit":
                return self.prev_state
        return self
