from .widgets import draw_box, draw_bar, term_print


def _stat_print(term, x, y, text):
    term_print(term, x, y, f"[font=sidebar]{text}")


class SidebarPanel:
    def render(self, term, rect, player_display):
        font = "sidebar"
        txt_col = "light blue"
        att_col = "light blue"
        def_col = "white"
        xp_col = "amber"
        val_col = "light grey"
        draw_box(term, rect)
        x, y = rect.x + 1, rect.y + 1
        _stat_print(
            term, x, y,
            f"[color={txt_col}]Health:[color={val_col}] {player_display.hp}/{player_display.max_hp} "
        )
        draw_bar(term, font, x+7, y, rect.w-9, player_display.hp,
                 player_display.max_hp, "dark red")
        y += 1
        _stat_print(
            term, x, y,
            f"[color={txt_col}]Oxygen:[color={val_col}] {player_display.oxy}/{player_display.max_oxy} "
        )
        draw_bar(term, font, x+7, y, rect.w-9, player_display.oxy,
                 player_display.max_oxy, "dark cyan")
        y += 2
        _stat_print(
            term, x, y,
            f"[color={att_col}]AW:[color={val_col}] {player_display.awareness:<4}"
            f"[color={att_col}]EQ:[color={val_col}] {player_display.equilibrium:<4}"
            f"[color={att_col}]RE:[color={val_col}] {player_display.reasoning:<4}"
            f"[color={att_col}]VI:[color={val_col}] {player_display.vigor}"
        )
        y += 1
        _stat_print(
            term, x, y,
            f"[color={def_col}]AV:[color={val_col}] {player_display.armor:<4}"
            f"[color={def_col}]EV:[color={val_col}] {player_display.evasion:<4}"
            f"[color={xp_col}]XL:[color={val_col}] {player_display.xp_level:<4}"
            f"[color={xp_col}]XP:[color={val_col}] {player_display.xp_percent}%"
        )
        y += 2
        _stat_print(
            term, x, y,
            f"[color={txt_col}]Main: "
            f"[color={player_display.main_hand.color}]"
            f"{player_display.main_hand.name}"
        )
        y += 1
        _stat_print(
            term, x, y,
            f"[color={txt_col}]Offhand: "
            f"[color={player_display.offhand.color}]"
            f"{player_display.offhand.name}"
        )

class LogPanel:
    def render(self, term, rect, log):
        draw_box(term, rect)
        x = rect.x * term.xs + 4
        y = rect.y * term.ys + 2
        w = rect.w * term.xs - 4
        h = rect.h + 3
        wrapped_msgs = []
        for msg in log.msgs[-h:]:
            wrapped_msgs += log._wrap(msg, w)
        wrapped_msgs = wrapped_msgs[-h:]
        term.color("white")
        y += 2
        for msg in wrapped_msgs:
            term.print(x, y, f"[font=gui]  {msg}")
            y += 2
