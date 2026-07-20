from .ecs.world import World
from .ecs.components import *
from .ecs.systems.input import Input
from .ecs.systems.fov import do_fov
from .ecs.systems.render import render_all, animate_projectile
from .ecs.systems.ai import take_monster_turns
from .ecs.systems.movement import try_move
from .ecs.systems.combat import fire_ranged
from .ecs.systems.combat_calculations import attack_weapon
from .ecs.systems.scheduler import (
    ActionClock,
    STANDARD_ACTION_COST,
    player_attack_cost,
)
from .ecs.systems.hud import get_player_stats
from .ecs.systems.inventory import pick_up, drop, equip_item, unequip_slot, use_consumable
from .map.derelict import Derelict
from .factories import spawn_actor, spawn_item, spawn_elevator
from .data.items import ITEM_KEYS
from .ui.layout import Camera, make_layout
from .ui.panels import SidebarPanel, LogPanel
from .ui.widgets import clear_area
from .ui.text_boxes import draw_inspect
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
        self.world.add(player, AbilityScores())
        self.world.add(player, Skills())
        self.world.add(player, Faction("player"))
        self.world.add(player, HP(100, 100))
        self.world.add(player, Oxygen(100, 100))
        self.world.add(player, Experience())
        self.world.add(player, Attack(5))
        self.world.add(player, Speed(1.0))
        self.player = player
        self.action_clock = ActionClock()
        self.ranged_target = None
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
        self.layout = make_layout(self.term)
        self.camera = Camera(
            self.layout.map_area, self.map.w, self.map.h
        )
        self._center_camera()

    def _populate_map(self):
        # TODO: stack items when duplicating in same spot (or increase count)
        pos = self.world.get(Position, self.player)
        z = self.map.z
        for r in self.map.rooms:
            num = min(r.size(), self.rng.randint(0, 2))
            for _ in range(num):
                x, y = self.rng.choice(list(r.inside()))
                # TODO: replace uniform selection with depth-weighted spawning
                kind = self.rng.choice(ITEM_KEYS)
                eid = spawn_item(self.world, kind, x, y, z)
                self.map.items[(x, y)].append(eid)
            if r.is_inside(pos.x, pos.y): continue
            num = min(r.size(), self.rng.randint(0, 3))
            for _ in range(num):
                x, y = self.rng.choice(list(r.inside()))
                if not self.map.blocked(x, y):
                    kind = self.rng.choice([
                        "skitterling", "mantis", "blightmoth"
                    ])
                    eid = spawn_actor(self.world, kind, x, y, z)
                    self.map.actors[x, y] = eid

    def _fov(self):
        pos = self.world.get(Position, self.player)
        radius = self.world.get(FOVRadius, self.player).radius
        do_fov(pos.x, pos.y, radius, self.map)

    def _center_camera(self):
        pos = self.world.get(Position, self.player)
        self.camera.center_on(pos.x, pos.y)

    def _render(self):
        self.term.clear()
        self._fov()
        self._center_camera()
        render_all(
            self.term, self.world, self.map, self.camera, self.show_all
        )
        stats = get_player_stats(self.world, self.player)
        self.sidebar.render(self.term, self.layout.sidebar, stats)
        self.logpanel.render(self.term, self.layout.log, self.log)
        self.term.refresh()

    def _animate_projectile(self, source, path, color):
        animate_projectile(
            self.term, self.world, self.map, self.camera,
            source, path, color
        )

    def spend_player_time(self, cost=STANDARD_ACTION_COST):
        self._center_camera()
        for _ in range(self.action_clock.spend(cost)):
            take_monster_turns(
                self.world, self.map, self.player, self.log,
                projectile_callback=self._animate_projectile
            )
            player_hp = self.world.get(HP, self.player)
            if player_hp is not None and player_hp.current <= 0:
                break

    def _move_action_cost(self, dx, dy):
        pos = self.world.get(Position, self.player)
        nx, ny = pos.x + dx, pos.y + dy
        if not self.map.in_bounds(nx, ny):
            return STANDARD_ACTION_COST
        target = self.map.actors[nx, ny]
        if target < 0:
            return STANDARD_ACTION_COST
        player_faction = self.world.get(Faction, self.player).tag
        target_faction = self.world.get(Faction, target)
        if target_faction is None or target_faction.tag == player_faction:
            return STANDARD_ACTION_COST
        return player_attack_cost(self.world, self.player, "melee")

    def _handle_player_cmd(self, cmd):
        if not cmd: return self
        match cmd[0]:
            case "move":
                _, dx, dy = cmd
                action_cost = self._move_action_cost(dx, dy)
                if try_move(self.world, self.player, dx, dy, self.map,
                            self.log):
                    self.spend_player_time(action_cost)
                return self
            case "wait":
                self.spend_player_time()
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
                        self.spend_player_time()
                    return self
                else:
                    # TODO: pick up menu needed if more than one item
                    item = items_xy[0]
                    if pick_up(self.world, self.map, self.player, item,
                               self.log):
                        self.spend_player_time()
                    return self
            case "inspect":
                return InspectState(self.term, self.world, self.map,
                                    self.player, self)
            case "target":
                if attack_weapon(self.world, self.player, "ranged") is None:
                    self.log.add("You are not wielding a ranged weapon.")
                    return self
                return TargetState(self.term, self.world, self.map,
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
        self.camera.map_w = self.map.w
        self.camera.map_h = self.map.h
        pos.x, pos.y, pos.z = x, y, new_z
        self.map.actors[pos.x, pos.y] = self.player
        self.spend_player_time()

    def tick(self):
        self._render()
        cmd = self.input.poll(self.term)
        return self._handle_player_cmd(cmd)

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
        self._update_target()
        self.prev_state = prev_state
        self.camera = prev_state.camera

    def _update_target(self):
        ents = self.map.inspectable_ents_at(self.world, self.x, self.y)
        if self.target not in ents:
            self.target = ents[0] if ents else None

    def _next_target(self):
        if not self.vis_ent:
            return None
        if self.target not in self.vis_ent:
            return min(
                self.vis_ent,
                key=lambda eid: (
                    self.world.get(Position, eid).x - self.x
                ) ** 2 + (
                    self.world.get(Position, eid).y - self.y
                ) ** 2
            )
        idx = self.vis_ent.index(self.target)
        return self.vis_ent[(idx + 1) % len(self.vis_ent)]

    def _update_xy(self, x, y):
        if self.map.in_bounds(x, y):
            self.x, self.y = x, y
            self._update_target()

    def _render(self):
        area = self.camera.viewport
        clear_area(self.term, area.x, area.y, area.w, area.h)
        render_all(self.term, self.world, self.map, self.camera)
        self.term.composition_on()
        if self.camera.contains(self.x, self.y):
            screen_x, screen_y = self.camera.world_to_screen(
                self.x, self.y
            )
            draw_inspect(self.term, screen_x, screen_y)
        self.term.composition_off()
        self.term.refresh()

    def tick(self):
        self._render()
        cmd = self.input.poll(self.term)
        if not cmd: return self
        if cmd[0] == "move":
            _, dx, dy = cmd
            self._update_xy(self.x + dx, self.y + dy)
        elif cmd[0] == "select":
            if self.target is not None:
                return DescMenu(self.term, self.world, self.target, self)
            tile_desc = self.map.tile_description(self.x, self.y)
            if tile_desc is not None:
                title, description = tile_desc
                return TileDescMenu(self.term, title, description, self)
        elif cmd[0] == "next":
            self.target = self._next_target()
            if self.target is not None:
                pos = self.world.get(Position, self.target)
                self.x, self.y = pos.x, pos.y
        elif cmd[0] == "quit":
            return self.prev_state
        return self


class TargetState():
    def __init__(self, term, world, game_map, player, prev_state):
        self.term = term
        self.input = Input("target", ["play_moves", "target", "next",
                                      "cancel"])
        self.world = world
        self.map = game_map
        self.player = player
        self.prev_state = prev_state
        self.camera = prev_state.camera
        player_pos = self.world.get(Position, self.player)
        self.targets = self._visible_enemies()
        remembered = self.prev_state.ranged_target
        if remembered in self.targets:
            self.target = remembered
        elif self.targets:
            self.target = min(
                self.targets,
                key=lambda eid: self._distance_sq(eid, player_pos.x,
                                                   player_pos.y)
            )
        else:
            self.target = None
        if self.target is not None:
            pos = self.world.get(Position, self.target)
            self.x, self.y = pos.x, pos.y
        else:
            self.x, self.y = player_pos.x, player_pos.y

    def _distance_sq(self, eid, x, y):
        pos = self.world.get(Position, eid)
        return (pos.x - x) ** 2 + (pos.y - y) ** 2

    def _visible_enemies(self):
        player_faction = self.world.get(Faction, self.player).tag
        enemies = []
        for eid, pos, faction, hp in self.world.view(
                Position, Faction, HP):
            if eid == self.player or pos.z != self.map.z:
                continue
            if faction.tag == player_faction or hp.current <= 0:
                continue
            if self.map.visible[pos.x, pos.y]:
                enemies.append(eid)
        return enemies

    def _target_at_cursor(self):
        eid = self.map.actors[self.x, self.y]
        if eid in self.targets:
            return eid
        return None

    def _next_target(self):
        self.targets = self._visible_enemies()
        if not self.targets:
            return None
        player_pos = self.world.get(Position, self.player)
        self.targets.sort(
            key=lambda eid: self._distance_sq(
                eid, player_pos.x, player_pos.y
            )
        )
        if self.target not in self.targets:
            return self.targets[0]
        index = self.targets.index(self.target)
        return self.targets[(index + 1) % len(self.targets)]

    def _move_cursor(self, dx, dy):
        x, y = self.x + dx, self.y + dy
        if self.map.in_bounds(x, y) and self.map.visible[x, y]:
            self.x, self.y = x, y
            self.targets = self._visible_enemies()
            self.target = self._target_at_cursor()

    def _render(self):
        area = self.camera.viewport
        clear_area(self.term, area.x, area.y, area.w, area.h)
        render_all(self.term, self.world, self.map, self.camera)
        self.term.composition_on()
        if self.camera.contains(self.x, self.y):
            screen_x, screen_y = self.camera.world_to_screen(
                self.x, self.y
            )
            draw_inspect(self.term, screen_x, screen_y)
        self.term.composition_off()
        self.term.refresh()

    def _animate_projectile(self, source, path, color):
        animate_projectile(
            self.term, self.world, self.map, self.camera,
            source, path, color
        )

    def tick(self):
        self._render()
        cmd = self.input.poll(self.term)
        if not cmd:
            return self
        if cmd[0] == "move":
            _, dx, dy = cmd
            self._move_cursor(dx, dy)
        elif cmd[0] == "next":
            self.target = self._next_target()
            if self.target is not None:
                pos = self.world.get(Position, self.target)
                self.x, self.y = pos.x, pos.y
        elif cmd[0] == "fire":
            player_pos = self.world.get(Position, self.player)
            if (self.x, self.y) == (player_pos.x, player_pos.y):
                self.prev_state.log.add("Select a target.")
                return self
            selected_target = self._target_at_cursor()
            action_cost = player_attack_cost(
                self.world, self.player, "ranged"
            )
            if not fire_ranged(
                    self.world, self.map, self.player, self.x, self.y,
                    self.prev_state.log,
                    projectile_callback=self._animate_projectile):
                return self.prev_state
            if selected_target in self._visible_enemies():
                self.prev_state.ranged_target = selected_target
            else:
                self.prev_state.ranged_target = None
            self.prev_state.spend_player_time(action_cost)
            return self.prev_state
        elif cmd[0] == "quit":
            return self.prev_state
        return self
