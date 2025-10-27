import numpy as np
from .widgets import draw_box, draw_bar, put

class SidebarPanel:
    def render(self, term, rect, player_stats):
        draw_box(term, rect)
        x, y = rect.x + 1, rect.y + 1
        draw_bar(term, x, y, rect.w - 2, player_stats.hp,
                 player_stats.max_hp, "dark red")
        y += 1
        draw_bar(term, x, y, rect.w - 2, player_stats.oxy,
                 player_stats.max_oxy, "cyan")

class LogPanel:
    def render(self, term, rect, log):
        draw_box(term, rect)
        x, y = rect.x + 2, rect.y + 1
        w, h = rect.w - 1, rect.h - 2
        wrapped_msgs = []
        for msg in log.msgs[-h:]:
            wrapped_msgs += log._wrap(msg, w)
        wrapped_msgs = wrapped_msgs[-h:]
        term.color("white")
        for msg in wrapped_msgs:
            term.print(x, y, f"[font=gui]{msg}")
            y += 1

