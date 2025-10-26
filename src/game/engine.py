from .terminal import Term
from .state import TitleState

def run():
    with Term() as term:
        state = TitleState(term)
        while state is not None:
            state = state.tick()
