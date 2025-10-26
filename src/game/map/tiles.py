import numpy as np
import random

class Map:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.floor = np.zeros((w, h), dtype=np.bool_)
        self.walls = np.zeros((w, h), dtype=np.bool_)
        self.doors = np.zeros((w, h), dtype=np.bool_)
        self.block = np.zeros((w, h), dtype=np.bool_)
        # tmp
        self.centers = np.zeros((w, h), dtype=np.bool_)
        self.peris = np.zeros((w, h), dtype=np.bool_)

    def in_bounds(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def blocked(self, x, y):
        return bool(self.block[x, y])

    def _pick_player_start(self, floor, seed):
        rng = random.Random(seed)
        px, py = rng.choice(list(floor))
        return px, py

    def generate_bsp(self, seed=None, reflect="none",
                     min_leaf=6, max_leaf=20,
                     min_room=1, max_room=10, border=1):
        from .bsp import generate_bsp
        centers, floor, walls, doors, peris = generate_bsp(
            self.w, self.h,
            seed=seed,
            min_leaf=min_leaf, max_leaf=max_leaf,
            min_room=min_room, max_room=max_room,
            border=border,
            reflect=reflect
        )
        # add floors
        fx, fy = zip(*floor)
        self.floor[list(fx), list(fy)] = True
        # add walls
        wx, wy = zip(*walls)
        self.walls[list(wx), list(wy)] = True
        self.block[list(wx), list(wy)] = True
        # add doors
        dx, dy = zip(*doors)
        self.doors[list(dx), list(dy)] = True
        # map edge blocks
        # TODO: change this to map space border later
        # TODO: move to wrapper to aall procgen methods
        self.block[0, :]  = True
        self.block[-1, :] = True
        self.block[:, 0]  = True
        self.block[:, -1] = True
        # player starts on a random floor tile
        self.px, self.py = self._pick_player_start(floor, seed)
        # tmp center check
        cx, cy = zip(*centers)
        self.centers[list(cx), list(cy)] = True
        # tmp peri check
        px, py = zip(*peris)
        self.peris[list(px), list(py)] = True

    def draw(self, term):
        xs, ys = term.xs, term.ys # x and y scale factors
        # floors
        term.color("darker grey")
        floorx, floory = np.nonzero(self.floor)
        for x, y in zip(floorx, floory):
            term.put(xs * int(x), ys * int(y), ".")
        # walls
        term.color("grey")
        wallx, wally = np.nonzero(self.walls)
        for x, y in zip(wallx, wally):
            term.put(xs * int(x), ys * int(y), "#")
        # walls
        term.color("dark blue")
        doorx, doory = np.nonzero(self.doors)
        for x, y in zip(doorx, doory):
            term.put(xs * int(x), ys * int(y), "+")
        # centers
        term.color("red")
        centerx, centery = np.nonzero(self.centers)
        for x, y in zip(centerx, centery):
            term.put(xs * int(x), ys * int(y), "*")
        # peris
        term.color("green")
        perix, periy = np.nonzero(self.peris)
        for x, y in zip(perix, periy):
            break
            term.put(xs * int(x), ys * int(y), "*")

