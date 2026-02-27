from search_sim.targets.basic_target import BasicTarget
from search_sim.targets.definitions.interfaces import Target
from search_sim.targets.definitions.types import TargetType
from typing import Optional

def target_factory(target_type: TargetType, id: str, location: tuple[float,float], value: float) -> Optional[Target]:
    match target_type:
        case TargetType.BASIC_TARGET:
            return BasicTarget(id, location, value)

        case _:
            raise ValueError(f"Unknown Target Type: {target_type}")
            return None