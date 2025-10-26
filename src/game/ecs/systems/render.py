from ..components import Position, Renderable

def draw(term, world, draw_map):
    xs, ys = term.xs, term.ys
    term.clear()
    draw_map(term)
    for eid, pos, ren in world.view(Position, Renderable):
        term.color(ren.color)
        term.put(term.xs*pos.x, term.ys*pos.y, ren.ch)
    term.refresh()
