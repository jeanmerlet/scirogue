from dataclasses import dataclass

@dataclass
class Rect:
    x: int; y: int
    w: int; h: int

@dataclass
class UILayout:
    map_area: Rect
    sidebar: Rect
    log: Rect

@dataclass
class Camera:
    viewport: Rect
    map_w: int
    map_h: int
    x: int = 0
    y: int = 0

    def center_on(self, world_x, world_y):
        self.x = world_x - self.viewport.w // 2
        self.y = world_y - self.viewport.h // 2

    def contains(self, world_x, world_y):
        return (
            self.x <= world_x < self.x + self.viewport.w
            and self.y <= world_y < self.y + self.viewport.h
        )

    def world_to_screen(self, world_x, world_y):
        return (
            self.viewport.x + world_x - self.x,
            self.viewport.y + world_y - self.y,
        )


def make_layout(term, map_w=35, map_h=22):
    map_w = min(map_w, term.w - 2)
    map_h = min(map_h, term.h - 2)
    map_area = Rect(0, 0, map_w, map_h)
    sidebar = Rect(map_w + 1, 0, term.w - map_w - 1, term.h)
    log = Rect(0, map_h + 1, map_w + 1, term.h - map_h - 1)
    return UILayout(map_area, sidebar, log)
