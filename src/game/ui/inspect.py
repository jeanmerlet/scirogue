from .layout import Rect
from .widgets import put, clear_area, term_print, draw_box
from ..ecs.components import Item, Name, Renderable, Description

def draw_inspect(term, x, y):
    term.color("light grey")
    put(term, x, y, "▒")

def _wrap_desc(desc, w):
    split_desc = desc.split(' ')
    last_word = split_desc[-1]
    out = []
    line = ""
    line_len = 0
    for word in split_desc:
        if line_len + len(word) + 3 > w * 2:
            out.append(line)
            line = word
            line_len = len(word)
        else:
            line += word
            line_len += len(word) + 1
        if word == last_word:
            out.append(line)
        else:
            line += " "
    return out

def _get_desc(world, eid, w):
    ttext = world.get(Name, eid).text.capitalize()
    tcolor = world.get(Renderable, eid).color
    title = f"[font=gui][color={tcolor}]{ttext}[/color]"
    tlen = len(ttext)
    desc = world.get(Description, eid).text
    desc = _wrap_desc(desc, w)
    cmds = ""
    return title, tlen, desc, cmds

def render_desc(term, world, eid):
    w = int(term.w * 0.33)
    h = int(term.h * 0.33)
    x = ((term.w - w) // 2)
    y = ((term.h - h) // 2)
    desc_area = Rect(x, y, w, h)
    clear_area(term, x, y, w, h)
    draw_box(term, desc_area)
    title, tlen, desc, cmds = _get_desc(world, eid, w - 2)
    # title
    y += 1
    centerx = term.w // 2
    term_print(term, centerx - (tlen // 2), y, title)
    # desc
    y += 1
    for line in desc:
        y += 1
        term_print(term, x + 2, y, f"[font=gui]{line}")
    # cmds
    term.refresh()
