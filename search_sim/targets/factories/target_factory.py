from search_sim.targets.basic_target import BasicTarget
from search_sim.targets.random_target import RandomTarget
from search_sim.targets.evasive_target import EvasiveTarget
from search_sim.targets.smart_target import SmartTarget
from search_sim.targets.definitions.interfaces import Target
from search_sim.targets.definitions.schema import TargetState, TargetType
from typing import Optional

def target_factory(
    target_type: TargetType, 
    target_state: TargetState
) -> Optional[Target]:
    match target_type:
        case TargetType.BASIC_TARGET:
            return BasicTarget(target_state)
        case TargetType.RANDOM_TARGET:
            return RandomTarget(target_state)
        case TargetType.EVASIVE_TARGET:
            return EvasiveTarget(target_state)
        case TargetType.SMART_TARGET:
            return SmartTarget(target_state)
        case _:
            raise ValueError(f"Unknown Target Type: {target_type}")
            return None