import numpy as np
import random

class Map:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.floor = np.zeros((w, h), dtype=np.bool_)
        self.walls = np.zeros((w, h), dtype=np.bool_)
        self.doors_open = np.zeros((w, h), dtype=np.bool_)
        self.doors_closed = np.zeros((w, h), dtype=np.bool_)
        self.windows = np.zeros((w, h), dtype=np.bool_)
        self.block = np.zeros((w, h), dtype=np.bool_)
        self.visible = np.zeros((w, h), dtype=np.bool_)
        self.explored = np.zeros((w, h), dtype=np.bool_)
        self.entities = np.full((w, h), -1, dtype=int)
        # for debugging
        self.centers = np.zeros((w, h), dtype=np.bool_)
        self.peris = np.zeros((w, h), dtype=np.bool_)
        # map edge
        self.edge = np.zeros((w, h), dtype=np.bool_)
        self.edge[0, :]  = True
        self.edge[-1, :] = True
        self.edge[:, 0]  = True
        self.edge[:, -1] = True

    def _clear_masks(self):
        self.floor.fill(False)
        self.walls.fill(False)
        self.doors_open.fill(False)
        self.doors_closed.fill(False)
        self.windows.fill(False)
        self.block.fill(False)
        self.centers.fill(False)
        self.peris.fill(False)

    def _pick_player_start(self, floor, seed):
        rng = random.Random(seed)
        px, py = rng.choice(list(floor))
        return px, py

    def opaque(self):
        return self.walls | self.edge | self.doors_closed

    def in_bounds(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def blocked(self, x, y):
        return bool(self.block[x, y] or self.edge[x, y] or
                    self.entities[x, y] >= 0)

    def open_door(self, x, y):
        self.doors_closed[x, y] = False
        self.doors_open[x, y] = True
        self.block[x, y] = False

    def generate_bsp(self, seed=None,
                     min_leaf=6, max_leaf=20,
                     min_rsize=1, max_rsize=10,
                     reflect="none", border=1):
        from .bsp import generate_bsp
        rooms, floor, walls, doors_closed, windows, centers, peris = generate_bsp(
            self.w, self.h, seed=seed,
            min_leaf=min_leaf, max_leaf=max_leaf,
            min_rsize=min_rsize, max_rsize=max_rsize,
            border=border, reflect=reflect
        )
        self.rooms = rooms
        self._clear_masks()
        # add floors
        fx, fy = zip(*floor)
        self.floor[list(fx), list(fy)] = True
        # player starts on a random floor tile
        self.px, self.py = self._pick_player_start(floor, seed)
        # add walls
        wx, wy = zip(*walls)
        self.walls[list(wx), list(wy)] = True
        self.block[list(wx), list(wy)] = True
        # add doors
        dx, dy = zip(*doors_closed)
        self.doors_closed[list(dx), list(dy)] = True
        self.block[list(dx), list(dy)] = True
        self.walls[list(dx), list(dy)] = False
        # add windows
        wx, wy = zip(*windows)
        self.windows[list(wx), list(wy)] = True
        self.block[list(wx), list(wy)] = True
        self.walls[list(dx), list(dy)] = False
        # room centers for debugging
        cx, cy = zip(*centers)
        self.centers[list(cx), list(cy)] = True
        # room perimeters for debugging
        px, py = zip(*peris)
        self.peris[list(px), list(py)] = True

    def draw(self, term):
        #self.visible = np.ones((self.w, self.h), dtype=np.bool_)
        xs, ys = term.xs, term.ys # x and y scale factors
        # floors
        term.color("grey")
        fx, fy = np.nonzero(self.floor & self.visible)
        for x, y in zip(fx, fy):
            term.put(xs * int(x), ys * int(y), ".")
        term.color("darker grey")
        fx, fy = np.nonzero(self.floor & ~self.visible &
                            self.explored)
        for x, y in zip(fx, fy):
            term.put(xs * int(x), ys * int(y), ".")
        # walls
        term.color("grey")
        wx, wy = np.nonzero(self.walls & self.visible)
        for x, y in zip(wx, wy):
            term.put(xs * int(x), ys * int(y), "#")
        term.color("darker grey")
        wx, wy = np.nonzero(self.walls & ~self.visible &
                            self.explored)
        for x, y in zip(wx, wy):
            term.put(xs * int(x), ys * int(y), "#")
        # doors
        term.color("dark blue")
        dx, dy = np.nonzero(self.doors_closed & self.visible)
        for x, y in zip(dx, dy):
            term.put(xs * int(x), ys * int(y), "+")
        dx, dy = np.nonzero(self.doors_open & self.visible)
        for x, y in zip(dx, dy):
            term.put(xs * int(x), ys * int(y), "-")
        term.color("darker grey")
        dx, dy = np.nonzero(self.doors_closed & ~self.visible &
                            self.explored)
        for x, y in zip(dx, dy):
            term.put(xs * int(x), ys * int(y), "+")
        dx, dy = np.nonzero(self.doors_open & ~self.visible &
                            self.explored)
        for x, y in zip(dx, dy):
            term.put(xs * int(x), ys * int(y), "-")
        # windows
        term.color("dark blue")
        wx, wy = np.nonzero(self.windows & self.visible)
        for x, y in zip(wx, wy):
            term.put(xs * int(x), ys * int(y), "o")
        term.color("darker grey")
        wx, wy = np.nonzero(self.windows & ~self.visible &
                            self.explored)
        for x, y in zip(wx, wy):
            term.put(xs * int(x), ys * int(y), "o")
        # centers (for debugging)
        term.color("red")
        cx, cy = np.nonzero(self.centers & self.visible)
        for x, y in zip(cx, cy):
            break
            term.put(xs * int(x), ys * int(y), "*")
        # perimeters (for debugging)
        term.color("green")
        px, py = np.nonzero(self.peris & self.visible)
        for x, y in zip(px, py):
            break
            term.put(xs * int(x), ys * int(y), "*")

