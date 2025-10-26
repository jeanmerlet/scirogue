import numpy as np

# multipliers for transforming coordinates to other octants
MULT = np.array([[1,  0,  0,  1, -1,  0,  0, -1],
                 [0,  1,  1,  0,  0, -1, -1,  0],
                 [0,  1, -1,  0,  0, -1,  1,  0],
                 [1,  0,  0, -1, -1,  0,  0,  1]], dtype=int)

def _light(x, y, visible):
    visible[x, y] = True

def _cast_light(visible, opaque, ox, oy, radius,
                row, start, end, xx, xy, yx, yy):
    if start < end:
        return

    radius_sq = radius**2
    for j in range(row, radius+1):
        out_of_bounds = False
        blocked = False
        dx = -j - 1
        dy = -j
        while dx <= 0:
            dx += 1
            X = ox + dx * xx + dy * xy
            Y = oy + dx * yx + dy * yy
            l_slope = (dx - 0.5)/(dy + 0.5)
            r_slope = (dx + 0.5)/(dy - 0.5)
            if start < r_slope:
                continue
            elif end > l_slope:
                break
            else:
                if dx**2 + dy**2 < radius_sq:
                    _light(X, Y, visible)
                if blocked:
                    if opaque[X, Y]:
                        new_start = r_slope
                        continue
                    else:
                        blocked = False
                        start = new_start
                else:
                    if opaque[X, Y] and j < radius:
                        blocked = True
                        _cast_light(visible, opaque, ox, oy, radius, j+1,
                                    start, l_slope, xx, xy, yx, yy)
                        new_start = r_slope
        if blocked:
            break

def do_fov(x, y, radius, game_map):
    visible = game_map.visible
    opaque = game_map.opaque()
    _light(x, y, visible)
    for octant in range(8):
        _cast_light(visible, opaque, x, y, radius, 1, 1.0, 0.0,
                    MULT[0, octant], MULT[1, octant],
                    MULT[2, octant], MULT[3, octant])

