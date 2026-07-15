from .widgets import draw_box, draw_bar, term_print

class SidebarPanel:
    def render(self, term, rect, player_stats):
        draw_box(term, rect)
        x, y = rect.x + 1, rect.y + 1
        draw_bar(term, x, y, rect.w - 2, player_stats.hp,
                 player_stats.max_hp, "dark red")
        y += 2
        draw_bar(term, x, y, rect.w - 2, player_stats.oxy,
                 player_stats.max_oxy, "dark cyan")
        y += 3
        term.color("white")
        term_print(
            term, x, y,
            f"AW: {player_stats.awareness:<3} "
            f"EQ: {player_stats.equilibrium}"
        )
        y += 1
        term_print(
            term, x, y,
            f"RE: {player_stats.reasoning:<3} "
            f"VI: {player_stats.vigor}"
        )
        y += 1
        term_print(term, x, y, f"Armor: {player_stats.armor}")
        y += 1
        term_print(term, x, y, f"Evasion: {player_stats.evasion}")
        y += 1
        term_print(term, x, y, f"XP: {player_stats.xp_percent} %")

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
