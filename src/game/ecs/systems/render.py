from ..components import Position, Renderable

def draw(term, world, draw_map, visible):
    xs, ys = term.xs, term.ys
    draw_map(term)
    batch = []
    for eid, pos, ren in world.view(Position, Renderable):
        if not visible[pos.x, pos.y]: continue
        batch.append((ren.order, pos, ren))
    batch.sort(key=lambda t: t[0])
    for _, pos, ren in batch:
        term.color(ren.color)
        term.put(term.xs*pos.x, term.ys*pos.y, ren.ch)
