from bearlibterminal import terminal as blt

class Key:
    LEFT        = 1001
    RIGHT       = 1002
    UP          = 1003
    DOWN        = 1004
    UP_LEFT     = 1005
    UP_RIGHT    = 1006
    DOWN_LEFT   = 1007
    DOWN_RIGHT  = 1008
    WAIT        = 1009
    QUIT        = 1010

    ALIASES = {
        LEFT:       (blt.TK_LEFT,  blt.TK_KP_4, ord('h')),
        RIGHT:      (blt.TK_RIGHT, blt.TK_KP_6, ord('l')),
        UP:         (blt.TK_UP,    blt.TK_KP_8, ord('k')),
        DOWN:       (blt.TK_DOWN,  blt.TK_KP_2, ord('j')),
        UP_LEFT:    (blt.TK_KP_7,  ord('y')),
        UP_RIGHT:   (blt.TK_KP_9,  ord('u')),
        DOWN_LEFT:  (blt.TK_KP_1,  ord('b')),
        DOWN_RIGHT: (blt.TK_KP_3,  ord('n')),
        WAIT:       (blt.TK_KP_5,  ord('.')),
        QUIT:       (blt.TK_Q,)
    }

REVERSE = {phys: logical
           for logical, phys_list in Key.ALIASES.items()
           for phys in phys_list}

def canonicalize(physical_key: int) -> int:
    return REVERSE.get(physical_key)


class Term:
    def __init__(self):
        self.font_path = "../assets/fonts/SpaceMono-Regular.ttf"
        self.xs = 2
        self.ys = 1
        self.w = 100
        self.h = 60

    def __enter__(self):
        blt.open()
        blt.set("window.title='scirogue'")
        blt.set(f"window.size={self.xs*self.w}x{self.ys*self.h}")
        blt.set("window.cellsize=8x16")
        blt.set(f"font: {self.font_path}, size=16, spacing={self.xs}x{self.ys}")
        blt.set(f"gui font: {self.font_path}, size=12")
        blt.refresh()
        return self

    def __exit__(self, exc_type, exc, traceback):
        blt.close()

    def clear(self):
        blt.clear()

    def put(self, x, y, ch):
        blt.put(x, y, ch)

    def put_ext(self, x, y, ch, corners, dx=0, dy=0):
        blt.put_ext(x, y, dx, dy, ch, corners)

    def print(self, x, y, text):
        blt.print(x, y, text)

    def color(self, color):
        blt.color(color)

    def refresh(self):
        blt.refresh()

    def read(self):
        return blt.read()
