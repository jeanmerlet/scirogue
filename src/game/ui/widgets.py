def put(term, x, y, ch):
    term.put(term.xs * x, term.ys * y, ch)

def draw_box(term, rect, color="light grey"):
    term.color(color)
    x, y, w, h = rect.x, rect.y, rect.w, rect.h
    put(term, x, y, "╔")
    put(term, x+w-1, y, "╗")
    put(term, x, y+h-1, "╚")
    put(term, x+w-1, y+h-1, "╝")
    for cx in range(x+1, x+w-1):
        put(term, cx, y, "═")
        put(term, cx, y+h-1, "═")
    for cy in range(y+1, y+h-1):
        put(term, x, cy, "║")
        put(term, x+w-1, cy, "║")

def draw_bar(term, x, y, w, cur, maxv, fg, bg="dark grey"):
    cur = max(0, min(cur, maxv))
    filled = 0 if maxv <= 0 else int(round((cur / maxv) * w))
    term.color(bg)
    for i in range(w):
        put(term, x + i, y, "#")
    term.color(fg)
    for i in range(filled):
        put(term, x + i, y, "#")
