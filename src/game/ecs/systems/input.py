from ...terminal import Key, canonicalize

class Input:
    def __init__(self, state="play"):
        self._stack = [state]
        self._maps = {
            "play": {
                Key.LEFT:       ("move", -1,  0),
                Key.RIGHT:      ("move",  1,  0),
                Key.UP:         ("move",  0, -1),
                Key.DOWN:       ("move",  0,  1),
                Key.UP_LEFT:    ("move", -1, -1),
                Key.UP_RIGHT:   ("move",  1, -1),
                Key.DOWN_LEFT:  ("move", -1,  1),
                Key.DOWN_RIGHT: ("move",  1,  1),
                Key.WAIT:       ("wait",),
                Key.QUIT:       ("quit",)
            }
        }

    def context(self):
        return self._stack[-1]

    def push(self, context):
        self._stack.append(context)

    def pop(self):
        if len(self._stack) > 1: self._stack.pop()

    def poll(self, term):
        k_phys = term.read()
        k = canonicalize(k_phys)
        return self._maps[self.context()].get(k, "noop")
