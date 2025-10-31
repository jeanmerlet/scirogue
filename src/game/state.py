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
from .ui.widgets import clear_area
from .ui.inspect import draw_inspect
from .ecs.systems.hud import get_player_stats
from .services.log import MessageLog
from .menu import InventoryMenu, DescMenu
from random import choice, randint
import numpy as np

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
                state = InspectState(self.term, self.world, self.map,
                                     self.player, self)
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
    def __init__(self, term, world, game_map, player, prev_state):
        self.term = term
        self.input = Input("inspect")
        self.world = world
        self.map = game_map
        self.player = player
        pos = self.world.get(Position, self.player)
        self.vis_ent = self.map.sorted_visible_entities(pos.x, pos.y)
        self.x, self.y = pos.x, pos.y
        self.target = None
        self.prev_state = prev_state
        self.prev_state.turn_taken = False

    def _next_target(self):
        num_ents = len(self.vis_ent)
        if num_ents == 0: return None
        if self.target is not None:
            idx = (self.vis_ent == self.target).argmax()
        else:
            return self.vis_ent[0]
        next_idx = (idx + 1) % num_ents
        return self.vis_ent[next_idx]

    def _update_xy(self, x, y):
        self.x = x if 0 <= x <= self.map.w else self.x
        self.y = y if 0 <= y <= self.map.h else self.y

    def _render(self):
        clear_area(self.term, 0, 0, self.map.w + 1, self.map.h + 1)
        sys_render.draw(self.term, self.world, self.map.draw, 
                        self.map.visible)
        self.term.composition_on()
        draw_inspect(self.term, self.x, self.y)
        self.term.composition_off()
        self.term.refresh()

    def tick(self):
        self._render()
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if cmd[0] == "move":
            _, dx, dy = cmd
            self._update_xy(self.x + dx, self.y + dy)
            if self.map.actors[self.x, self.y] > 0:
                self.target = self.map.actors[self.x, self.y]
            else:
                self.target = None
        elif cmd[0] == "select":
            return DescMenu(self.term, self.world, self.target, self)
        elif cmd[0] == "next":
            self.target = self._next_target()
            if self.target is not None:
                pos = self.world.get(Position, self.target)
                self.x, self.y = pos.x, pos.y
        elif cmd[0] == "quit":
            return self.prev_state
        return self
