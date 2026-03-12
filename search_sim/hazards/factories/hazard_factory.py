from search_sim.hazards.hazards import RunningWater, StandingWater, Tree, Undergrowth, Boulder
from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.types import HazardType
from typing import Optional

def hazard_factory(hazard_type: HazardType, id: str, location: tuple[float,float]) -> Optional[Hazard]:
    match hazard_type:
        case HazardType.RUNNING_WATER:
            return RunningWater(id, location)
        
        case HazardType.STANDING_WATER:
            return StandingWater(id, location)
        
        case HazardType.TREE:
            return Tree(id, location)
        
        case HazardType.UNDERGROWTH:
            return Undergrowth(id, location)
        
        case HazardType.BOULDER:
            return Boulder(id, location)

        case _:
            raise ValueError(f"Unknown Target Type: {hazard_type}")
            return None