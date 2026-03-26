from search_sim.hazards.hazards import RunningWater, StandingWater, Tree, Undergrowth, Boulder
from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.schema import HazardType, HazardState
from typing import Optional

def hazard_factory(hazard_type: HazardType, hazard_state: HazardState) -> Optional[Hazard]:
    match hazard_type:
        case HazardType.RUNNING_WATER:
            return RunningWater(hazard_state)
        
        case HazardType.STANDING_WATER:
            return StandingWater(hazard_state)
        
        case HazardType.TREE:
            return Tree(hazard_state)
        
        case HazardType.UNDERGROWTH:
            return Undergrowth(hazard_state)
        
        case HazardType.BOULDER:
            return Boulder(hazard_state)

        case _:
            raise ValueError(f"Unknown Target Type: {hazard_type}")
            return None