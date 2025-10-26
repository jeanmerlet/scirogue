from .ecs.systems.input import Input
from .ecs.systems import render as sys_render
from .ecs.systems import movement as sys_move
from .ecs.world import World
from .ecs.components import Position, Renderable, Actor, FOVRadius
from .map.tiles import Map
from .ecs.systems.fov import do_fov

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
        self.map.generate_bsp(seed=None, reflect="h")
        self.world = World()
        player = self.world.create()
        startx, starty = self.map.px, self.map.py
        self.world.add(player, Position(startx, starty))
        self.world.add(player, FOVRadius(8))
        self.world.add(player, Renderable("@", "amber"))
        self.world.add(player, Actor())
        self.player = player
        pos = self.world.get(Position, self.player)
        radius = self.world.get(FOVRadius, self.player).radius
        do_fov(pos.x, pos.y, radius, self.map)
        sys_render.draw(self.term, self.world, self.map.draw)

    def tick(self):
        intent = self.input.poll(self.term)

        match intent[0]:
            case "move":
                _, dx, dy = intent
                sys_move.move(self.world, self.player, dx, dy,
                              self.map.doors_closed,
                              self.map.open_door,
                              self.map.blocked) 
            case "open_menu":
                return MenuState(self.term, self.input)
            case "quit":
                return None

        pos = self.world.get(Position, self.player)
        radius = self.world.get(FOVRadius, self.player).radius
        do_fov(pos.x, pos.y, radius, self.map)
        sys_render.draw(self.term, self.world, self.map.draw)

        return self

class MenuState(BaseState):
    def __init__(self, term):
        super().__init__(term)
        self.input = Input("menu")

    def tick(self):
       pass 
