from collections import defaultdict

class World:
    def __init__(self):
        self._next_eid = 0
        self.components = defaultdict(dict)

    def create(self):
        self._next_eid += 1
        return self._next_eid - 1

    def destroy(self, eid):
        for comp_dict in self.components.values():
            comp_dict.pop(eid, None)

    def add(self, eid, comp):
        self.components[type(comp)][eid] = comp

    def remove(self, eid, comp_type):
        self.components[comp_type].pop(eid, None)

    def get(self, comp_type, eid):
        return self.components[comp_type].get(eid)

    def has(self, eid, comp_type):
        return eid in self.components[comp_type]

    def view(self, *types):
        sets = [set(self.components[t]) for t in types]
        for eid in set.intersection(*sets):
            yield(eid, *[self.components[t][eid] for t in types])

    def duplicate(self, eid):
        dup_eid = self.create()
        pass
