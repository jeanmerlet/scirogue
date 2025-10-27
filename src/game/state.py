from .ecs.systems.input import Input
from .ecs.systems import render as sys_render
from .ecs.systems import movement as sys_move
from .ecs.systems.ai import take_monster_turns
from .ecs.world import World
from .ecs.components import *
from .map.tiles import Map
from .ecs.systems.fov import do_fov
from .factories.spawner import spawn_monster
from random import choice, randint

class BaseState:
    def __init__(self, term):
        self.term = term

    def tick(self):
        raise NotImplementedError

class TitleState(BaseState):
    def tick(self):
        blt = self.term
        blt.clear()
        blt.refresh()
        return PlayState(blt)

class PlayState(BaseState):
    def __init__(self, term):
        super().__init__(term)
        self.input = Input("play")
        self.map = Map(80, 60)
        self.map.generate_bsp(seed=102, reflect="h")
        self.world = World()
        player = self.world.create()
        startx, starty = self.map.px, self.map.py
        self.world.add(player, Position(startx, starty))
        self.map.entities[startx, starty] = player
        self.world.add(player, FOVRadius(10))
        self.world.add(player, Renderable("@", "amber", 3))
        self.world.add(player, Blocks())
        self.world.add(player, Actor())
        self.world.add(player, Faction("player"))
        self.world.add(player, HP(100, 100))
        self.world.add(player, Attack(5))
        self.world.add(player, Speed(1.0))
        self.player = player
        self._populate_map()
        self._render()

    def _populate_map(self):
        pos = self.world.get(Position, self.player)
        for r in self.map.rooms:
            if r.is_inside(pos.x, pos.y): continue
            num = min(r.size(), randint(0, 3))
            num = min(r.size(), randint(4, 4))
            for _ in range(num):
                x, y = choice(list(r.inside()))
                if not self.map.blocked(x, y):
                    kind = choice(["skitterling", "skittermaw",
                                   "skitterseer"])
                    eid = spawn_monster(self.world, kind, x, y)
                    self.map.entities[x, y] = eid

    def _fov(self):
        pos = self.world.get(Position, self.player)
        radius = self.world.get(FOVRadius, self.player).radius
        do_fov(pos.x, pos.y, radius, self.map)

    def _render(self):
        self._fov()
        sys_render.draw(self.term, self.world, self.map.draw, 
                        self.map.visible)

    def _take_player_turn(self):
        intent = self.input.poll(self.term)
        match intent[0]:
            case "move":
                _, dx, dy = intent
                sys_move.try_move(self.world, self.player,
                                  dx, dy, self.map, self.log)
            case "open_menu":
                return MenuState(self.term, self.input)
            case "quit":
                return None
        self._fov()
        return self

    def _take_nonplayer_turns(self):
        take_monster_turns(self.world, self.map, self.player, log=self.log)

    def tick(self):
        self.log = getattr(self, "log", [])
        state = self._take_player_turn()
        self._take_nonplayer_turns()
        self._render()
        return state

class MenuState(BaseState):
    def __init__(self, term):
        super().__init__(term)
        self.input = Input("menu")

    def tick(self):
       pass 
