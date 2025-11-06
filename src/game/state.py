from .ecs.world import World
from .ecs.components import *
from .ecs.systems.input import Input
from .ecs.systems.fov import do_fov
from .ecs.systems.render import render_all
from .ecs.systems.ai import take_monster_turns
from .ecs.systems.movement import try_move
from .ecs.systems.hud import get_player_stats
from .ecs.systems.inventory import pick_up, drop, equip_item, unequip_slot, use_consumable
from .map.derelict import Derelict
from .factories import spawn_actor, spawn_item, spawn_elevator
from .ui.layout import make_layout
from .ui.panels import SidebarPanel, LogPanel
from .ui.widgets import clear_area
from .ui.description import draw_inspect
from .services.log import MessageLog
from .menu import *
import numpy as np
import random

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
        self.input = Input("play", ["play_moves", "play"])
        self.rng = random.Random()
        self.rng.seed(103)
        self.world = World()
        player = self.world.create()
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
        self.show_all = False
        self.derelict = Derelict(self.rng)
        self.derelict.gen_maps(self.world)
        px, py, pz = self.derelict.player_start()
        self.world.add(player, Position(px, py, pz))
        self.map = self.derelict.maps[pz]
        self.map.actors[px, py] = player
        self._populate_map()
        self.log = MessageLog()
        self.sidebar = SidebarPanel()
        self.logpanel = LogPanel()
        sidebar_w = term.w - self.map.w
        log_h = term.h - self.map.h
        self.layout = make_layout(self.term, self.map.w, self.map.h,
                                  sidebar_w, log_h)

    def _populate_map(self):
        # TODO: stack items when duplicating in same spot (or increase count)
        pos = self.world.get(Position, self.player)
        z = self.map.z
        for r in self.map.rooms:
            num = min(r.size(), self.rng.randint(0, 2))
            for _ in range(num):
                x, y = self.rng.choice(list(r.inside()))
                kind = self.rng.choice(["stimpack", "crowbar", "coil_rifle"])
                eid = spawn_item(self.world, kind, x, y, z)
                self.map.items[(x, y)].append(eid)
            if r.is_inside(pos.x, pos.y): continue
            num = min(r.size(), self.rng.randint(0, 3))
            for _ in range(num):
                x, y = self.rng.choice(list(r.inside()))
                if not self.map.blocked(x, y):
                    kind = self.rng.choice(["skitterling", "skittermaw",
                                            "skitterseer"])
                    eid = spawn_actor(self.world, kind, x, y, z)
                    self.map.actors[x, y] = eid

    def _fov(self):
        pos = self.world.get(Position, self.player)
        radius = self.world.get(FOVRadius, self.player).radius
        do_fov(pos.x, pos.y, radius, self.map)

    def _render(self):
        self.term.clear()
        self._fov()
        render_all(self.term, self.world, self.map, self.show_all)
        stats = get_player_stats(self.world, self.player)
        self.sidebar.render(self.term, self.layout.sidebar, stats)
        self.logpanel.render(self.term, self.layout.log, self.log)
        self.term.refresh()

    def _handle_player_cmd(self, cmd):
        if not cmd: return self
        match cmd[0]:
            case "move":
                _, dx, dy = cmd
                if try_move(self.world, self.player, dx, dy, self.map,
                            self.log):
                    self.turn_taken = True
                return self
            case "wait":
                self.turn_taken = True
                return self
            case "pick_up":
                pos = self.world.get(Position, self.player)
                items_xy = self.map.items[(pos.x, pos.y)]
                num_items = len(items_xy)
                if num_items == 0:
                    return self
                elif num_items == 1:
                    item = items_xy[0]
                    if pick_up(self.world, self.map, self.player, item,
                               self.log):
                        self.turn_taken = True
                    return self
                else:
                    # TODO: pick up menu needed if more than one item
                    item = items_xy[0]
                    if pick_up(self.world, self.map, self.player, item,
                               self.log):
                        self.turn_taken = True
                    return self
            case "inspect":
                return InspectState(self.term, self.world, self.map,
                                    self.player, self)
            case "drop":
                return DropMenu(self.term, self.world, self.map, self.player,
                                self.log, self)
            case "inv_menu":
                return InventoryMenu(self.term, self.world, self.map,
                                     self.player, self.log, self)
            case "equipment_menu":
                return EquipmentMenu(self.term, self.world, self.map,
                                     self.player, self.log, self)
            case "equip_menu":
                return EquipMenu(self.term, self.world, self.map,
                                 self.player, self.log, self)
            case "unequip_menu":
                return UnequipMenu(self.term, self.world, self.map,
                                   self.player, self.log, self)
            case "use_elevator":
                pos = self.world.get(Position, self.player)
                elev = self.map.elevators[pos.x, pos.y]
                if elev < 0:
                    self.log.add("There's no elevator here.")
                    return self
                return ElevatorMenu(self.term, self.world, self.map,
                                    self.derelict, self.player, elev,
                                    self.log, self)
            case "game_menu":
                # nothing for now
                return self
            case "show_all":
                self.show_all = True if self.show_all == False else False
                return self
            case "quit":
                return None

    def change_level(self, new_z, x, y):
        pos = self.world.get(Position, self.player)
        self.map.actors[pos.x, pos.y] = -1
        self.map = self.derelict.maps[new_z]
        self.map.z = new_z
        pos.x, pos.y, pos.z = x, y, new_z
        self.map.actors[pos.x, pos.y] = self.player
        self.turn_taken = True

    def tick(self):
        self._render()
        self.turn_taken = False
        cmd = self.input.poll(self.term)
        state = self._handle_player_cmd(cmd)
        if self.turn_taken:
            take_monster_turns(self.world, self.map, self.player, self.log)
        return state

class MenuState():
    def __init__(self, term):
        self.term = term
        self.input = Input("menu")

    def tick(self):
       pass 

class InspectState():
    def __init__(self, term, world, game_map, player, prev_state):
        self.term = term
        self.input = Input("inspect", ["play_moves", "inspect", "next",
                                       "cancel"])
        self.world = world
        self.map = game_map
        self.player = player
        pos = self.world.get(Position, self.player)
        self.vis_ent = self.map.sorted_vis_ents(self.world, pos.x, pos.y)
        self.x, self.y = pos.x, pos.y
        self.target = None
        self.prev_state = prev_state
        self.prev_state.turn_taken = False

    def _next_target(self):
        num_ents = len(self.vis_ent)
        if num_ents == 0: return None
        if self.target:
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
        render_all(self.term, self.world, self.map)
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
            if self.target:
                return DescMenu(self.term, self.world, self.target, self)
        elif cmd[0] == "next":
            self.target = self._next_target()
            if self.target:
                pos = self.world.get(Position, self.target)
                self.x, self.y = pos.x, pos.y
        elif cmd[0] == "quit":
            return self.prev_state
        return self
