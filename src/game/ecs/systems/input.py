#from ...terminal import Key, canonicalize
from bearlibterminal import terminal as blt

class Input:
    def __init__(self, state="play"):
        self.state = state
        self._maps = {
            "play": {
                blt.TK_LEFT:    ("move", -1,  0),
                blt.TK_KP_4:    ("move", -1,  0),
                blt.TK_H:       ("move", -1,  0),
                blt.TK_RIGHT:   ("move",  1,  0),
                blt.TK_KP_6:    ("move",  1,  0),
                blt.TK_L:       ("move",  1,  0),
                blt.TK_UP:      ("move",  0, -1),
                blt.TK_KP_8:    ("move",  0, -1),
                blt.TK_K:       ("move",  0, -1),
                blt.TK_DOWN:    ("move",  0,  1),
                blt.TK_KP_2:    ("move",  0,  1),
                blt.TK_J:       ("move",  0,  1),
                blt.TK_KP_7:    ("move", -1, -1),
                blt.TK_Y:       ("move", -1, -1),
                blt.TK_KP_9:    ("move",  1, -1),
                blt.TK_U:       ("move",  1, -1),
                blt.TK_KP_1:    ("move", -1,  1),
                blt.TK_B:       ("move", -1,  1),
                blt.TK_KP_3:    ("move",  1,  1),
                blt.TK_N:       ("move",  1,  1),
                blt.TK_KP_5:    ("wait",),
                blt.TK_PERIOD:  ("wait",),
                blt.TK_D:       ("drop",),
                blt.TK_G:       ("pick_up",),
                blt.TK_I:       ("inv_menu",),
                blt.TK_Q:       ("quit",),
                blt.TK_ESCAPE:  ("game_menu",)
            },
            "inventory": {
                blt.TK_UP:      "up",
                blt.TK_DOWN:    "down",
                blt.TK_ENTER:   "select",
                blt.TK_ESCAPE:  "quit",
            }
        }

    def poll(self, term):
        key = term.read()
        return self._maps[self.state].get(key, "noop")
