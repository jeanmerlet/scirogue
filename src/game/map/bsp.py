import random

class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def center(self):
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        return (cx, cy)

    def is_inside(self, x, y):
        return (self.x <= x < self.x + self.w and
                self.y <= y < self.y + self.h)

    def perimeter(self, corners=False):
        c = 1 if corners else 0
        perimeter = set()
        for x in range(self.x - c, self.x + self.w + c):
            perimeter.add((x, self.y - 1))
            perimeter.add((x, self.y + self.h))
        for y in range(self.y - c, self.y + self.h + c):
            perimeter.add((self.x - 1 , y))
            perimeter.add((self.x + self.w, y))
        return perimeter

    def subdivide(self, vertical, cut):
        if vertical:
            w1 = cut - self.x
            w2 = (self.x + self.w) - cut
            recta = Room(self.x, self.y, w1, self.h)
            rectb = Room(cut, self.y, w2, self.h)
        else:
            h1 = cut - self.y
            h2 = (self.y + self.h) - cut
            recta = Room(self.x, self.y, self.w, h1)
            rectb = Room(self.x, cut, self.w, h2)
        return recta, rectb

class BSPNode:
    def __init__(self, rect):
        self.rect = rect
        self.left = None
        self.right = None
        self.room = None

def _split(node, rng, min_leaf=6, max_leaf=20):
    """Recursively split a node into two children until it
    gets smallish. min_leaf/max_leaf loosely govern split sizes.
    """
    rect = node.rect
    if rect.w < max_leaf and rect.h < max_leaf:
        return

    # Choose split orientation biased to the larger dimension
    vertical = rect.w > rect.h
    # Don’t split leaves too small:
    if vertical and rect.w < 2 * min_leaf:
        vertical = False
    if not vertical and rect.h < 2 * min_leaf:
        vertical = True
    if rect.w < 2 * min_leaf and rect.h < 2 * min_leaf:
        return

    if vertical:
        cut = rng.randrange(rect.x + min_leaf, rect.x + rect.w - min_leaf)
    else:
        cut = rng.randrange(rect.y + min_leaf, rect.y + rect.h - min_leaf)

    left_rect, right_rect = rect.subdivide(vertical, cut)
    node.left, node.right = BSPNode(left_rect), BSPNode(right_rect)

    _split(node.left, rng, min_leaf, max_leaf)
    _split(node.right, rng, min_leaf, max_leaf)

def _carve_rooms(node, rng, min_rsize=1, max_rsize=10, border=1):
    """Assign a room to each leaf BSP node."""
    if node.left or node.right:
        if node.left: _carve_rooms(node.left, rng, min_rsize,
                                   max_rsize, border)
        if node.right: _carve_rooms(node.right, rng, min_rsize,
                                    max_rsize, border)
        return

    # leaf: pick a room size and position it
    # within the leaf with a small border
    leaf = node.rect
    usable_w = max(0, leaf.w - 2 * border)
    usable_h = max(0, leaf.h - 2 * border)
    rw = min(max_rsize, usable_w)
    rh = min(max_rsize, usable_h)
    if rw < min_rsize or rh < min_rsize:
        node.room = None
        return
    w = rng.randint(min_rsize, rw)
    h = rng.randint(min_rsize, rh)
    # rooms can only be 1x1, not 1xn or nx1
    if w == 1 or h == 1:
        w = h = 1
    x = rng.randint(leaf.x + border, leaf.x + leaf.w - border - w)
    y = rng.randint(leaf.y + border, leaf.y + leaf.h - border - h)
    node.room = Room(x, y, w, h)

def _collect_rooms(node, out):
    if node.left or node.right:
        if node.left:  _collect_rooms(node.left, out)
        if node.right: _collect_rooms(node.right, out)
    else:
        if node.room:
            out.append(node.room)

def _carve_corridor(floor, a, b):
    # L-shaped corridor between centers of rooms a and b
    ax, ay = a.center()
    bx, by = b.center()
    # carve horizontal then vertical
    xstep = 1 if bx >= ax else -1
    for x in range(ax, bx + xstep, xstep):
        floor.add((x, ay))
    ystep = 1 if by >= ay else -1
    for y in range(ay, by + ystep, ystep):
        floor.add((bx, y))

def _connect_rooms(node, floor):
    # recursively connect rooms along the BSP tree
    if not (node.left and node.right):
        return
    # connect deepest children first
    _connect_rooms(node.left, floor)
    _connect_rooms(node.right, floor)
    # find a room in left subtree and a room in right subtree
    left_rooms, right_rooms = [], []
    _collect_rooms(node.left, left_rooms)
    _collect_rooms(node.right, right_rooms)
    if not left_rooms or not right_rooms:
        return
    # pick nearest pair
    _carve_corridor(floor, left_rooms[0], right_rooms[0])

def _place_walls(floor, w, h):
    walls = set()
    neigh = (
        (-1,-1), (0,-1), (1,-1),
        (-1, 0),         (1, 0),
        (-1, 1), (0, 1), (1, 1),
    )
    for (x, y) in floor:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in floor:
                walls.add((nx, ny))
    return walls

def _place_doors(rooms, floor, walls):
    doors = set()
    # max doors per room side if not replacing floor
    dmax = 1
    for r in rooms:
        peri = r.perimeter()
        n, s, e, w = 0, 0, 0, 0
        for (x, y) in peri:
            place_door = False
            # north-south doors
            if (((x, y-1) in floor and(x, y+1) in floor) and not
               ((x-1, y) in floor or (x+1, y) in floor)):
                place_door = True
                # count north doors
                if r.is_inside(x, y-1):
                    n += 1
                    if n > dmax and (x, y) not in floor:
                        place_door = False
                # count south doors
                if r.is_inside(x, y+1):
                    s += 1
                    if s > dmax and (x, y) not in floor:
                        place_door = False
            # east-west doors
            if (((x-1, y) in floor and (x+1, y) in floor) and not
               ((x, y-1) in floor or (x, y+1) in floor)):
                place_door = True
                # count east doors
                if r.is_inside(x-1, y):
                    e += 1
                    if e > dmax and (x, y) not in floor:
                        place_door = False
                # count west doors
                if r.is_inside(x+1, y):
                    w += 1
                    if w > dmax and (x, y) not in floor:
                        place_door = False
            if place_door:
                doors.add((x, y))
    return doors

def _reflect_tiles(tiles, w, h, gaph, gapv, mode):
    reflected = []
    for tileset in tiles:
        if mode == "none":
            return tiles
        ref_tileset = set(tileset)
        if mode in ["h", "hv"]:
            for (x, y) in list(tileset):
                rx = w - x - gaph
                ref_tileset.add((rx, y))
        if mode == "v":
            for (x, y) in list(tileset):
                ry = h - y - gapv
                ref_tileset.add((x, ry))
        if mode == "hv":
            for (x, y) in list(ref_tileset):
                ry = h - y - gapv
                ref_tileset.add((x, ry))
        reflected.append(ref_tileset)
    return reflected

def _reflect_rooms(rooms, w, h, gaph, gapv, mode):
    if mode == "none":
        return rooms
    out = set()
    for r in rooms:
        xs = [r.x]
        ys = [r.y]
        if mode in ["h", "hv"]:
            xs.append((w - r.x - r.w - gaph + 1))
        if mode in ["v", "hv"]:
            ys.append((h - r.y - r.h - gapv + 1))
        for x in xs:
            for y in ys:
                out.add((x, y, r.w, r.h))
    return [Room(x, y, w, h) for (x, y, w, h) in out]

def _connect_center(floor, walls, doors, w, h, edgeh, edgev, mode):
    max_doors = 2
    if mode == "none":
        return doors
    if mode in ["h", "hv"]:
        num_doors = 0
        mid_walls = [xy for xy in walls if xy[0] == edgeh]
        for (x, y) in  mid_walls:
            if num_doors == max_doors: break
            if (((x-1, y) in floor and (x+1, y) in floor) and not
               ((x, y-1) in floor or (x, y+1) in floor)):
                walls.remove((x, y))
                doors.add((x, y))
                num_doors += 1
    if mode in ["v", "hv"]:
        num_doors = 0
        mid_walls = [xy for xy in walls if xy[1] == edgev]
        for (x, y) in  mid_walls:
            if num_doors == max_doors: break
            if (((x, y-1) in floor and(x, y+1) in floor) and not
               ((x-1, y) in floor or (x+1, y) in floor)):
                walls.remove((x, y))
                doors.add((x, y))
                num_doors += 1
    return doors

def generate_bsp(w, h, seed=None,
                 min_leaf=6, max_leaf=20,
                 min_rsize=1, max_rsize=10,
                 border=1, reflect="none",
                 margin_min=5, margin_max=10):
    rng = random.Random(seed)
    margin = rng.randint(margin_min, margin_max)
    # allow for smaller margins if map is tiny
    max_allowed = min((w - 2) // 2, (h - 2) // 2) 
    margin = max(0, min(margin, max_allowed))
    # halve width and/or height if reflecting
    mapw = w
    maph = h
    if reflect in ["h", "hv"]:
        mapw = w // 2
    if reflect in ["v", "hv"]:
        maph = h // 2
    # build the BSP only inside the inner rectangle
    inner_x = margin
    inner_y = margin
    inner_w = mapw - 2 * margin
    inner_h = maph - 2 * margin
    if reflect in ["h", "hv"]:
        inner_w = mapw - margin
    if reflect in ["v", "hv"]:
        inner_h = maph - margin
    # run BSP
    root = BSPNode(Room(inner_x + 1, inner_y + 1,
                        inner_w - 2, inner_h - 2))
    _split(root, rng, min_leaf=min_leaf, max_leaf=max_leaf)
    _carve_rooms(root, rng, min_rsize=min_rsize,
                 max_rsize=max_rsize, border=border)
    rooms = []
    _collect_rooms(root, rooms)
    # add floor based on rooms
    floor = set()
    for r in rooms:
        for x in range(r.x, r.x + r.w):
            for y in range(r.y, r.y + r.h):
                floor.add((x, y))
    _connect_rooms(root, floor)
    walls = _place_walls(floor, w, h)
    doors = _place_doors(rooms, floor, walls)
    # reflect if reflecting
    edgeh = max([xy[0] for xy in walls])
    edgev = max([xy[1] for xy in walls])
    gaph = 2 * (mapw - edgeh)
    gapv = 2 * (maph - edgev)
    tiles = [floor, walls, doors]
    floor, walls, doors = _reflect_tiles(tiles, w, h, gaph, gapv, reflect)
    rooms = _reflect_rooms(rooms, w, h, gaph, gapv, reflect)
    doors = _connect_center(floor, walls, doors, w, h, edgeh, edgev, reflect)
    # for debugging
    centers = [r.center() for r in rooms]
    peris = set()
    for r in rooms:
        for p in r.perimeter():
            peris.add(p)
    return centers, floor, walls, doors, peris
