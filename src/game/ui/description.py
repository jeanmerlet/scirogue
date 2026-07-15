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
        if line_len + len(word) + 3 > w:
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

def _render_desc(term, title_text, title_color, description):
    w = int(term.w * 0.33)
    h = int(term.h * 0.33)
    x = ((term.w - w) // 2)
    y = ((term.h - h) // 2)
    desc_area = Rect(x, y, w, h)
    clear_area(term, x, y, w, h)
    draw_box(term, desc_area)

    title_text = title_text.capitalize()
    title = f"[font=gui][color={title_color}]{title_text}[/color]"
    desc = _wrap_desc(description, (w - 2) * term.xs)

    y += 1
    title_w = (len(title_text) + term.xs - 1) // term.xs
    centerx = term.w // 2
    term_print(term, centerx - title_w // 2, y, title)
    y += 1
    for line in desc:
        y += 1
        term_print(term, x + 2, y, f"[font=gui]{line}")
    term.refresh()


def render_desc(term, world, eid):
    title = world.get(Name, eid).text
    color = world.get(Renderable, eid).color
    description = world.get(Description, eid)
    text = description.text if description else ""
    _render_desc(term, title, color, text)


def render_tile_desc(term, title, description):
    _render_desc(term, title, "light grey", description)
