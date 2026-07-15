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
        max_x = max(0, self.map_w - self.viewport.w)
        max_y = max(0, self.map_h - self.viewport.h)
        self.x = max(0, min(world_x - self.viewport.w // 2, max_x))
        self.y = max(0, min(world_y - self.viewport.h // 2, max_y))

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


def make_layout(term, map_w=40, map_h=22):
    map_w = min(map_w, term.w - 2)
    map_h = min(map_h, term.h - 2)
    map_area = Rect(0, 0, map_w, map_h)
    sidebar = Rect(map_w + 1, 0, term.w - map_w - 1, term.h)
    log = Rect(0, map_h + 1, map_w + 1, term.h - map_h - 1)
    return UILayout(map_area, sidebar, log)
