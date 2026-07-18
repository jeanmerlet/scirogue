from bearlibterminal import terminal as blt

class Term:
    def __init__(self):
        self.font_path = "../assets/fonts/CourierPrime-Regular.ttf"
        self.bold_font_path = "../assets/fonts/CourierPrime-Bold.ttf"
        self.xs = 8
        self.ys = 4
        self.gui_xs = 2
        self.gui_ys = 1
        self.gui_line_ys = 2
        self.sidebar_xs = 3
        self.sidebar_ys = 2
        self.w = 50
        self.h = 30

    def __enter__(self):
        blt.open()
        blt.set("window.title='scirogue'")
        blt.set(f"window.size={self.xs*self.w}x{self.ys*self.h}")
        blt.set("window.cellsize=4x8")
        blt.set(f"font: {self.font_path}, size=32, spacing={self.xs}x{self.ys}")
        blt.set(
            f"bold font: {self.bold_font_path}, size=32, "
            f"spacing={self.xs}x{self.ys}"
        )
        blt.set(
            f"gui font: {self.font_path}, size=12, "
            f"spacing={self.gui_xs}x{self.gui_ys}"
        )
        blt.set(
            f"sidebar font: {self.font_path}, size=16, "
            f"spacing={self.sidebar_xs}x{self.sidebar_ys}"
        )
        blt.refresh()
        return self

    def __exit__(self, exc_type, exc, traceback):
        blt.close()

    def clear(self):
        blt.clear()

    def clear_area(self, x, y, w, h):
        blt.clear_area(x, y, w, h)

    def composition_on(self):
        blt.composition(1)
        
    def composition_off(self):
        blt.composition(0)

    def put(self, x, y, ch):
        blt.put(int(x), int(y), ch)

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
