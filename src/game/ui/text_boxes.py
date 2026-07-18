from math import ceil
from textwrap import wrap

from .layout import Rect
from .widgets import clear_area, draw_box, put
from ..ecs.components import Description, Name, Renderable


HORIZONTAL_PADDING_CHARS = 2


def draw_inspect(term, x, y):
    term.color("light grey")
    put(term, x, y, "▒")


def gui_text_width(term, text):
    """Return the width of plain GUI-font text in logical cells."""
    return ceil(len(text) * term.gui_xs / term.xs)


def gui_chars_in_width(term, logical_width):
    """Return the GUI-font characters that fit in a logical width."""
    return max(0, logical_width * term.xs // term.gui_xs)


def centered_rect(term, width, height, vertical_divisor=2):
    x = (term.w - width) // 2
    y = (term.h - height) // vertical_divisor
    return Rect(x, y, width, height)


def _gui_print(term, x, y, text):
    """Print GUI-font text using raw terminal coordinates."""
    term.print(x, y, f"[font=gui]{text}")


def _raw_bounds(term, rect):
    return (
        rect.x * term.xs,
        rect.y * term.ys,
        rect.w * term.xs,
        rect.h * term.ys,
    )


def draw_modal_frame(term, rect, title, title_color="white"):
    """Clear and draw a framed text box with an exactly centered title."""
    clear_area(term, rect.x, rect.y, rect.w, rect.h)
    draw_box(term, rect)

    left, top, width, _ = _raw_bounds(term, rect)
    title_width = len(title) * term.gui_xs
    title_x = left + (width - title_width) // 2
    title_y = top + term.ys
    _gui_print(
        term, title_x, title_y,
        f"[color={title_color}]{title}[/color]",
    )

    content_x = left + term.xs + HORIZONTAL_PADDING_CHARS * term.gui_xs
    content_y = title_y + term.ys
    return content_x, content_y


def _description_lines(term, description, rect):
    interior_width = max(0, rect.w - 2)
    max_chars = max(
        1,
        gui_chars_in_width(term, interior_width)
        - 2 * HORIZONTAL_PADDING_CHARS,
    )
    return wrap(description, width=max_chars) if description else []


def _render_desc(term, title_text, title_color, description):
    width = max(8, int(term.w * 0.33))
    height = max(6, int(term.h * 0.33))
    rect = centered_rect(term, width, height)
    title_text = title_text.capitalize()
    content_x, content_y = draw_modal_frame(
        term, rect, title_text, title_color
    )

    for line in _description_lines(term, description, rect):
        _gui_print(term, content_x, content_y, line)
        content_y += term.gui_ys
    term.refresh()


def render_desc(term, world, eid):
    title = world.get(Name, eid).text
    color = world.get(Renderable, eid).color
    description = world.get(Description, eid)
    text = description.text if description else ""
    _render_desc(term, title, color, text)


def render_tile_desc(term, title, description):
    _render_desc(term, title, "light grey", description)


def _menu_size(term, title, lines, content_width):
    text_width = max(content_width, len(title))
    cursor_width = 2
    inner_chars = (
        text_width + cursor_width + 2 * HORIZONTAL_PADDING_CHARS
    )
    width = ceil(inner_chars * term.gui_xs / term.xs) + 2

    title_height = term.ys
    entries_height = max(1, len(lines)) * term.gui_ys
    inner_height = title_height + term.gui_ys + entries_height
    height = ceil(inner_height / term.ys) + 2
    return width, height


def draw_menu(term, title, lines, content_width, selected_idx):
    width, height = _menu_size(term, title, lines, content_width)
    rect = centered_rect(term, width, height, vertical_divisor=3)
    content_x, content_y = draw_modal_frame(term, rect, title)

    cursor_x = content_x
    line_x = content_x + 2 * term.gui_xs
    for i, line in enumerate(lines):
        if i == selected_idx:
            _gui_print(term, cursor_x, content_y, ">")
        _gui_print(term, line_x, content_y, line)
        content_y += term.gui_ys
    term.refresh()
