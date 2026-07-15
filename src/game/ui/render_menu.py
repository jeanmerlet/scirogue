from .widgets import clear_area, term_print, put, draw_box
from .layout import Rect
from math import ceil

def draw_menu(term, title, lines, w, selected_idx):
    w = ceil(w / term.xs) + 3
    h = len(lines) + 5
    x = ((term.w - w) // 2)
    y = ((term.h - h) // 3)
    inv_area = Rect(x, y, w, h)
    clear_area(term, x, y, w, h)
    draw_box(term, inv_area)
    # title
    y += 1
    title_w = ceil(len(title) / term.xs)
    centerx = term.w // 2
    term.color("white")
    term_print(
        term, centerx - title_w // 2, y, f"[font=gui]{title}"
    )
    # entries
    y += 2
    for i, line in enumerate(lines):
        if i == selected_idx:
            put(term, x + 1, y, ">")
            term_print(term, x + 3, y, f"[font=gui]{line}")
        else:
            term_print(term, x + 3, y, f"[font=gui]{line}")
        y += 1
    term.refresh()
