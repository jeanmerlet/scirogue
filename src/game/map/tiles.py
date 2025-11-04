from ..ecs.components import Position, Description, Name
from collections import defaultdict
import numpy as np

class Map:
    def __init__(self, rng, w, h, z):
        self.rng = rng
        self.w, self.h, self.z = w, h, z
        self.floor = np.zeros((w, h), dtype=np.bool_)
        self.walls = np.zeros((w, h), dtype=np.bool_)
        self.doors_open = np.zeros((w, h), dtype=np.bool_)
        self.doors_closed = np.zeros((w, h), dtype=np.bool_)
        self.windows = np.zeros((w, h), dtype=np.bool_)
        self.block = np.zeros((w, h), dtype=np.bool_)
        self.visible = np.zeros((w, h), dtype=np.bool_)
        self.explored = np.zeros((w, h), dtype=np.bool_)
        self.actors = np.full((w, h), -1, dtype=int)
        self.elevators = np.full((w, h), -1, dtype=int)
        self.items = defaultdict(list) 
        # map edge
        self.edge = np.zeros((w, h), dtype=np.bool_)
        self.edge[0, :]  = True
        self.edge[-1, :] = True
        self.edge[:, 0]  = True
        self.edge[:, -1] = True
        # for debugging
        self.centers = np.zeros((w, h), dtype=np.bool_)
        self.peris = np.zeros((w, h), dtype=np.bool_)
        self.show_all = False

    def _clear_masks(self):
        self.floor.fill(False)
        self.walls.fill(False)
        self.doors_open.fill(False)
        self.doors_closed.fill(False)
        self.windows.fill(False)
        self.block.fill(False)
        self.centers.fill(False)
        self.peris.fill(False)

    def opaque(self):
        return self.walls | self.edge | self.doors_closed

    def in_bounds(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def blocked(self, x, y):
        return bool(self.block[x, y] or self.edge[x, y] or
                    self.actors[x, y] >= 0)

    def rand_floor_xy(self, unblocked=True):
        fx, fy = np.nonzero(self.floor)
        while True:
            i = self.rng.randrange(fx.size)
            x, y = int(fx[i]), int(fy[i])
            if not unblocked or not self.blocked(x, y):
                return x, y

    def sorted_vis_ents(self, world, cx, cy):
        ents = []
        dists = []
        for eid, pos, _, _ in world.view(Position, Description, Name):
            if pos.z != self.z: continue
            if not self.visible[pos.x, pos.y]: continue
            ents.append(eid)
            dists.append((cx-pos.x)**2 + (cy-pos.y)**2)
        ents = np.array(ents)[np.argsort(dists)]
        return ents

    def open_door(self, x, y):
        self.doors_closed[x, y] = False
        self.doors_open[x, y] = True
        self.block[x, y] = False

    def generate_map(self, reflect, kind="bsp", min_rsize=1, max_rsize=10):
        if kind == "bsp":
            from .bsp import generate_bsp
            tiles = generate_bsp(self.rng, self.w, self.h, reflect,
                                 min_rsize, max_rsize)
        self.rooms = tiles["rooms"]
        self._clear_masks()
        # add floors
        fx, fy = zip(*tiles["floor"])
        self.floor[list(fx), list(fy)] = True
        # add walls
        wx, wy = zip(*tiles["walls"])
        self.walls[list(wx), list(wy)] = True
        self.block[list(wx), list(wy)] = True
        # add doors
        if tiles["doors"]:
            dx, dy = zip(*tiles["doors"])
            self.doors_closed[list(dx), list(dy)] = True
            self.block[list(dx), list(dy)] = True
            self.walls[list(dx), list(dy)] = False
        # add windows
        if tiles["windows"]:
            wx, wy = zip(*tiles["windows"])
            self.windows[list(wx), list(wy)] = True
            self.block[list(wx), list(wy)] = True
            self.walls[list(wx), list(wy)] = False
        # room centers for debugging
        cx, cy = zip(*tiles["centers"])
        self.centers[list(cx), list(cy)] = True
        # room perimeters for debugging
        px, py = zip(*tiles["perims"])
        self.peris[list(px), list(py)] = True
