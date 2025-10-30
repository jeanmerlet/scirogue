from .widgets import clear_area, term_print, put, draw_box
from .layout import Rect

def render_inventory(term, lines, selected_idx=None):
    w = int(term.w * 0.66)
    h = int(term.h * 0.66)
    x = ((term.w - w) // 2)
    y = ((term.h - h) // 2)
    inv_area = Rect(x, y, w, h)
    clear_area(term, x, y, w, h)
    draw_box(term, inv_area)
    # title
    y += 1
    centerx = term.w // 2
    title = 'Inventory'
    term.color("white")
    term_print(term, centerx - len(title) // 2, y, f"[font=gui]{title}")
    # entries
    y += 2
    for i, line in enumerate(lines):
        if selected_idx is not None and i == selected_idx:
            put(term, x + 1, y, ">")
            term_print(term, x + 3, y, f"[font=gui]{line}")
        else:
            term_print(term, x + 3, y, f"[font=gui]{line}")
        y += 1
    term.refresh()
