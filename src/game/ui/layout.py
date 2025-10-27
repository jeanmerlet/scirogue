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

def make_layout(term, map_w, map_h, sidebar_w, log_h):
    total_w = map_w + sidebar_w
    total_h = map_h + log_h
    map_area = Rect(0, 0, map_w, map_h)
    sidebar  = Rect(map_w + 1, 0, sidebar_w - 1, total_h)
    log      = Rect(0, map_h + 1, map_w + 1, log_h - 1)
    return UILayout(map_area, sidebar, log)

