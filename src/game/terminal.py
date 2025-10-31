from bearlibterminal import terminal as blt

class Term:
    def __init__(self):
        self.font_path = "../assets/fonts/CourierPrime-Regular.ttf"
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

    def clear_area(self, x, y, w, h):
        blt.clear_area(x, y, w, h)

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
