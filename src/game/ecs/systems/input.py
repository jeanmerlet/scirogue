from bearlibterminal import terminal as blt

class Input:
    def __init__(self, state, domains):
        self.state = state
        self.cmd_domains = {
            "play_moves": {
                blt.TK_LEFT:      ("move", -1,  0),
                blt.TK_KP_4:      ("move", -1,  0),
                blt.TK_H:         ("move", -1,  0),
                blt.TK_RIGHT:     ("move",  1,  0),
                blt.TK_KP_6:      ("move",  1,  0),
                blt.TK_L:         ("move",  1,  0),
                blt.TK_UP:        ("move",  0, -1),
                blt.TK_KP_8:      ("move",  0, -1),
                blt.TK_K:         ("move",  0, -1),
                blt.TK_DOWN:      ("move",  0,  1),
                blt.TK_KP_2:      ("move",  0,  1),
                blt.TK_J:         ("move",  0,  1),
                blt.TK_KP_7:      ("move", -1, -1),
                blt.TK_Y:         ("move", -1, -1),
                blt.TK_KP_9:      ("move",  1, -1),
                blt.TK_U:         ("move",  1, -1),
                blt.TK_KP_1:      ("move", -1,  1),
                blt.TK_B:         ("move", -1,  1),
                blt.TK_KP_3:      ("move",  1,  1),
                blt.TK_N:         ("move",  1,  1),
            },
            "play": {
                blt.TK_KP_5:      ("wait",),
                blt.TK_PERIOD:    ("wait",),
                blt.TK_KP_PERIOD: ("wait",),
                blt.TK_D:         ("drop",),
                blt.TK_G:         ("pick_up",),
                blt.TK_I:         ("inv_menu",),
                blt.TK_Q:         ("quit",),
                blt.TK_X:         ("inspect",),
                blt.TK_E:         ("equipment_menu",),
                blt.TK_P:         ("equip_menu",),
                blt.TK_R:         ("unequip_menu",),
                blt.TK_GRAVE:     ("show_all",),
                blt.TK_ESCAPE:    ("game_menu",),
                ord(">"):         ("use_elevator",)
            },
            "menu": {
                blt.TK_UP:        ("up",),
                blt.TK_DOWN:      ("down",),
                blt.TK_ENTER:     ("select",),
            },
            "inspect": {
                blt.TK_V:         ("select",),
                blt.TK_ENTER:     ("select",),
            },
            "next": {
                blt.TK_TAB:       ("next",),
            },
            "cancel": {
                blt.TK_ESCAPE:    ("quit",)
            }
        }
        self.cmd_domains["letters"] = {}
        for i in range(blt.TK_A, blt.TK_Z + 1):
            self.cmd_domains["letters"][i] = (chr(i + 93),)
        self.cmd_domains["numbers"] = {}
        for i in range(blt.TK_1, blt.TK_0 + 1):
            if i != blt.TK_0:
                self.cmd_domains["numbers"][i] = (chr(i + 19),)
            else:
                self.cmd_domains["numbers"][i] = (chr(i + 9),)
        for i in range(blt.TK_KP_1, blt.TK_KP_0 + 1):
            if i != blt.TK_KP_0:
                self.cmd_domains["numbers"][i] = (chr(i - 40),)
            else:
                self.cmd_domains["numbers"][i] = (chr(i - 50),)
        self.cmds = {}
        for domain in domains:
            for k, v in self.cmd_domains[domain].items():
                self.cmds[k] = v

    def poll(self, term):
        key = term.read()
        if blt.check(blt.TK_SHIFT):
            return self.cmds.get(blt.state(blt.TK_CHAR))
        return self.cmds.get(key)
