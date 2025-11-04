from .tiles import Map
from dataclasses import dataclass, field
from ..factories import spawn_elevator

@dataclass
class ElevatorShaft:
    shaft_id: int
    landings: dict = field(default_factory=dict) # level: (x, y)

class Derelict:
    def __init__(self, rng):
        self.name = "derelict"
        self.rng = rng
        self.maps = []
        self.shafts = {} # shaft_id: ElevatorShaft(shaft_id, landings)

    def _place_elevators(self, world, min_shafts=1, max_shafts=4):
        n_levels = len(self.maps)
        n_shafts = self.rng.randint(min_shafts, max_shafts)
        shaft_id = 0
        for _ in range(n_shafts):
            k = self.rng.randint(2, n_levels)
            coverage = sorted(self.rng.sample(range(n_levels), k))
            landings = {}
            for level in coverage:
                x, y = self.maps[level].rand_floor_xy()
                landings[level] = (x, y)
            self.shafts[shaft_id] = ElevatorShaft(shaft_id, landings)
            shaft_id += 1
        for sid, shaft in self.shafts.items():
            for level, (x,y) in shaft.landings.items():
                eid = spawn_elevator(world, self, sid, level, x, y)
                self.maps[level].elevators[x, y] = eid

    def player_start(self):
        start_level_idx = self.rng.randint(0, len(self.maps) - 1)
        start_x, start_y = self.maps[start_level_idx].rand_floor_xy()
        return start_x, start_y, start_level_idx

    def gen_maps(self, world, min_level=2, max_level=5):
        n_level = self.rng.randint(min_level, max_level)
        map_w, map_h = 80, 52
        for i in range(n_level):
            level_map = Map(self.rng, map_w, map_h, i)
            reflect = self.rng.choice(["h", "v", "hv"])
            level_map.generate_map(reflect)
            self.maps.append(level_map)
        self._place_elevators(world)
