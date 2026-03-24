from search_sim.hazards.hazards import RunningWater, StandingWater, Tree, Undergrowth, Boulder
from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.schema import HazardType, HazardState
from typing import Optional

def hazard_factory(hazard_type: HazardType, state: HazardState) -> Optional[Hazard]:
    match hazard_type:
        case HazardType.RUNNING_WATER:
            return RunningWater(id, state)
        
        case HazardType.STANDING_WATER:
            return StandingWater(id, state)
        
        case HazardType.TREE:
            return Tree(id, state)
        
        case HazardType.UNDERGROWTH:
            return Undergrowth(id, state)
        
        case HazardType.BOULDER:
            return Boulder(id, state)

        case _:
            raise ValueError(f"Unknown Target Type: {hazard_type}")
            return None