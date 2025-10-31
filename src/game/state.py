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
from .ecs.systems.hud import get_player_stats
from .services.log import MessageLog
from .inventory_state import InventoryMenu
from random import choice, randint

class TitleState():
    def __init__(self, term):
        self.term = term

    def tick(self):
        self.term.clear()
        self.term.refresh()
        return PlayState(self.term)

class PlayState():
    def __init__(self, term):
        self.term = term
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

    def _handle_player_cmd(self, cmd):
        if not cmd: return False
        match cmd[0]:
            case "move":
                _, dx, dy = cmd
                return sys_move.try_move(self.world, self.player,
                                         dx, dy, self.map, self.log)
            case "wait":
                return True
            case "pick_up":
                # TODO: pick up menu needed if more than one item
                pos = self.world.get(Position, self.player)
                items_xy = self.map.items[(pos.x, pos.y)]
                num_items = len(items_xy)
                if num_items == 0:
                    return False
                else:
                    item = items_xy[0]
                    return pick_up(self.world, self.player, item, self.log)
            case "drop":
                # drop menu needed
                return False
            case "inspect":
                state = InspectState(self.term, self.world, self.player,
                                     self.log, self)
                return ("switch", state)
            case "inv_menu":
                menu = InventoryMenu(self.term, self.world, self.player,
                                     self.log, self)
                return ("switch", menu)
            case "game_menu":
                # nothing for now
                return False
            case "quit":
                return ("switch", None)
        return self

    def tick(self):
        self._render()
        cmd = self.input.poll(self.term)
        outcome = self._handle_player_cmd(cmd)
        if isinstance(outcome, tuple) and outcome[0] == "switch":
            return outcome[1]
        if outcome or self.turn_taken:
            take_monster_turns(self.world, self.map, self.player, self.log)
        return self

class MenuState():
    def __init__(self, term):
        self.term = term
        self.input = Input("menu")

    def tick(self):
       pass 

class InspectState():
    def __init__(self, term):
        self.term = term
        self.input = Input("inspect")
        self.world = world
        self.map = game_map
        self.player = player
        pos = self.world.get(Position, self.player)
        self.x, self.y = pos.x, pos.y

    def _update_xy(self, x, y):
        self.x = x if 0 <= x <= game_map.w
        self.y = y if 0 <= y <= game_map.h

    def tick(self):
        render_inspect(x, y)
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if cmd[0] == "move":
            _, dx, dy = cmd
            self._update_xy(self.x + dx, self.y + dy)
        elif cmd[0] == "enter":
            
        elif cmd[0] == "next":
            
        elif cmd[0] == "quit":
            return self.prev_state
        return self

