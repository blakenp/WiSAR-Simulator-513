"""Running water hazard class for e.g. a river or creek"""

from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.types import HazardType

class RunningWater(Hazard):
    def __init__(self, id, location):
        self.id = id
        self.location = location

    def get_id(self) -> str:
        return self.id

    def get_location(self) -> tuple[float,float]:
        return self.location

    def get_type(self) -> HazardType:
        return HazardType.RUNNING_WATER
    
"""Standing water hazard class for e.g. a pond or lake"""

"""Separate from running water just in case I guess"""

from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.types import HazardType

class StandingWater(Hazard):
    def __init__(self, id, location):
        self.id = id
        self.location = location

    def get_id(self) -> str:
        return self.id

    def get_location(self) -> tuple[float,float]:
        return self.location

    def get_type(self) -> HazardType:
        return HazardType.STANDING_WATER
    
"""Tree hazard class"""

"""Could be a single tree if the grid size is small enough, or a particularly dense stand of trees"""

from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.types import HazardType

class Tree(Hazard):
    def __init__(self, id, location):
        self.id = id
        self.location = location

    def get_id(self) -> str:
        return self.id

    def get_location(self) -> tuple[float,float]:
        return self.location

    def get_type(self) -> HazardType:
        return HazardType.TREE
    
"""Undergrowth hazard class"""

from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.types import HazardType

class Undergrowth(Hazard):
    def __init__(self, id, location):
        self.id = id
        self.location = location

    def get_id(self) -> str:
        return self.id

    def get_location(self) -> tuple[float,float]:
        return self.location

    def get_type(self) -> HazardType:
        return HazardType.UNDERGROWTH
    
"""Boulder hazard class"""

from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.types import HazardType

class Boulder(Hazard):
    def __init__(self, id, location):
        self.id = id
        self.location = location

    def get_id(self) -> str:
        return self.id

    def get_location(self) -> tuple[float,float]:
        return self.location

    def get_type(self) -> HazardType:
        return HazardType.BOULDER