from ..components import Position, Renderable
import numpy as np
import time

PROJECTILE_FRAME_SECONDS = 0.025

def render_tiles(term, tiles, vis, expl, vis_color, xs, ys, ch, camera):
    x0 = max(0, camera.x)
    y0 = max(0, camera.y)
    x1 = max(x0, min(camera.map_w, camera.x + camera.viewport.w))
    y1 = max(y0, min(camera.map_h, camera.y + camera.viewport.h))
    tiles = tiles[x0:x1, y0:y1]
    vis = vis[x0:x1, y0:y1]
    expl = expl[x0:x1, y0:y1]
    term.color(vis_color)
    all_x, all_y = np.nonzero(tiles & vis)
    for x, y in zip(all_x, all_y):
        screen_x = camera.viewport.x + x0 - camera.x + int(x)
        screen_y = camera.viewport.y + y0 - camera.y + int(y)
        term.put(xs * screen_x, ys * screen_y, ch)
    term.color("darker grey")
    all_x, all_y = np.nonzero(tiles & ~vis & expl)
    for x, y in zip(all_x, all_y):
        screen_x = camera.viewport.x + x0 - camera.x + int(x)
        screen_y = camera.viewport.y + y0 - camera.y + int(y)
        term.put(xs * screen_x, ys * screen_y, ch)

def render_entities(term, world, z_level, vis, expl, xs, ys, camera):
    batch = []
    for eid, pos, ren in world.view(Position, Renderable):
        if pos.z != z_level: continue
        batch.append((ren.order, pos, ren))
    batch.sort(key=lambda t: t[0])
    for _, pos, ren in batch:
        x, y = pos.x, pos.y
        if not camera.contains(x, y):
            continue
        if vis[x, y]:
            term.color(ren.color)
        elif not vis[x, y] and expl[x, y]:
            term.color("darker grey")
        else:
            continue
        screen_x, screen_y = camera.world_to_screen(x, y)
        term.put(xs * screen_x, ys * screen_y, ren.ch)

def render_all(term, world, game_map, camera, show_all=False, debug=False):
    if show_all:
        vis = np.ones((game_map.w, game_map.h), dtype=np.bool_)
    else:
        vis = game_map.visible
    expl = game_map.explored
    xs, ys = term.xs, term.ys
    render_tiles(
        term, game_map.floor, vis, expl, "grey", xs, ys, ".", camera
    )
    render_tiles(
        term, game_map.walls, vis, expl, "grey", xs, ys, "#", camera
    )
    render_tiles(
        term, game_map.doors_closed, vis, expl, "grey", xs, ys, "+",
        camera
    )
    render_tiles(
        term, game_map.doors_open, vis, expl, "grey", xs, ys, "/",
        camera
    )
    render_tiles(
        term, game_map.windows, vis, expl, "grey", xs, ys, "0", camera
    )
    if debug:
        render_tiles(
            term, game_map.centers, vis, expl, "red", xs, ys, "*",
            camera
        )
        render_tiles(
            term, game_map.peris, vis, expl, "green", xs, ys, "*",
            camera
        )
    render_entities(
        term, world, game_map.z, vis, expl, xs, ys, camera
    )


def _projectile_glyph(source, target):
    dx = target[0] - source[0]
    dy = target[1] - source[1]
    if dx == 0:
        return "|"
    if dy == 0:
        return "-"
    return "\\" if (dx > 0) == (dy > 0) else "/"


def animate_projectile(term, world, game_map, camera, source, path, color):
    if not path:
        return
    glyph = _projectile_glyph(source, path[-1])
    for x, y in path:
        if not game_map.visible[x, y] or not camera.contains(x, y):
            continue
        term.clear_area(
            camera.viewport.x * term.xs,
            camera.viewport.y * term.ys,
            camera.viewport.w * term.xs,
            camera.viewport.h * term.ys,
        )
        render_all(term, world, game_map, camera)
        term.composition_on()
        term.color(color)
        screen_x, screen_y = camera.world_to_screen(x, y)
        term.print(term.xs * screen_x, term.ys * screen_y,
                   f"[font=bold]{glyph}")
        term.composition_off()
        term.refresh()
        time.sleep(PROJECTILE_FRAME_SECONDS)

    term.clear_area(
        camera.viewport.x * term.xs,
        camera.viewport.y * term.ys,
        camera.viewport.w * term.xs,
        camera.viewport.h * term.ys,
    )
    render_all(term, world, game_map, camera)
    term.refresh()
