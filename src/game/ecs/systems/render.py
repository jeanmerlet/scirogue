from ..components import Position, Renderable
import numpy as np

def render_tiles(term, tiles, vis, expl, vis_color, xs, ys, ch):
    term.color(vis_color)
    all_x, all_y = np.nonzero(tiles & vis)
    for x, y in zip(all_x, all_y):
        term.put(xs * x, ys * y, ch)
    term.color("darker grey")
    all_x, all_y = np.nonzero(tiles & ~vis & expl)
    for x, y in zip(all_x, all_y):
        term.put(xs * x, ys * y, ch)

def render_entities(term, world, z_level, vis, expl, xs, ys):
    batch = []
    for eid, pos, ren in world.view(Position, Renderable):
        if pos.z != z_level: continue
        batch.append((ren.order, pos, ren))
    batch.sort(key=lambda t: t[0])
    for _, pos, ren in batch:
        x, y = pos.x, pos.y
        if vis[x, y]:
            term.color(ren.color)
        elif not vis[x, y] and expl[x, y]:
            term.color("darker grey")
        else:
            continue
        term.put(xs * x, ys * y, ren.ch)

def render_all(term, world, game_map, show_all=False, debug=False):
    if show_all:
        vis = np.ones((game_map.w, game_map.h), dtype=np.bool_)
    else:
        vis = game_map.visible
    expl = game_map.explored
    xs, ys = term.xs, term.ys
    render_tiles(term, game_map.floor, vis, expl, "grey", xs, ys, ".")
    render_tiles(term, game_map.walls, vis, expl, "grey", xs, ys, "#")
    render_tiles(term, game_map.doors_closed, vis, expl, "grey", xs, ys, "+")
    render_tiles(term, game_map.doors_open, vis, expl, "grey", xs, ys, "/")
    render_tiles(term, game_map.windows, vis, expl, "grey", xs, ys, "0")
    if debug:
        render_tiles(term, game_map.centers, vis, expl, "red", xs, ys, "*")
        render_tiles(term, game_map.peris, vis, expl, "green", xs, ys, "*")
    render_entities(term, world, game_map.z, vis, expl, xs, ys)
