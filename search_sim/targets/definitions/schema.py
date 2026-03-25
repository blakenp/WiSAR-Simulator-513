from search_sim.agents.definitions.interfaces import Agent
# from search_sim.targets.definitions.interfaces import Target
from search_sim.hazards.definitions.interfaces import Hazard
from dataclasses import dataclass
from enum import Enum

class TargetType(Enum):
    """Types of targets we want to simulate"""

    BASIC_TARGET = "basic_target"
    RANDOM_TARGET = "random_target"
    EVASIVE_TARGET = "evasive_target"
    SMART_TARGET = "smart_target"

@dataclass(frozen=True)
class TargetState:
    """Immutable state of a target.

    Attributes:
        target_id: Unique identifier for target.
        x: X position in grid cells.
        y: Y position in grid cells.
        value: Value of the target (e.g. importance, reward).
        traversable_hazards: All hazard types the target can navigate through.
        heading: Heading in degrees (0-360).
        speed_mps: Current speed in meters per second.
        max_speed: maximum speed the target can move.
        awareness_radius: distance around the target within which it can perceive its surroundings.
        nearby_agents: All agents within awareness_radius.
        nearby_targets: All other targets within awareness_radius.
        nearby_hazards: All hazards within awareness_radius.
    """

    id: str
    x: float
    y: float
    type: TargetType
    value: float
    traversable_hazards: list[Hazard]
    heading: float
    speed_mps: float
    max_speed: float
    awareness_radius: float
    nearby_agents: list[Agent]
    nearby_targets: list["Target"] # TODO: This creates a circular dependency. We may want to move TargetState to its own file to avoid this.
    nearby_hazards: list[Hazard]

@dataclass(frozen=True)
class TargetAction:
    """The 'Intent' of a target for the next step.
    
    Attributes:
        target_heading: Heading of where the target wants to move
        target_speed: How fast the target wants to move to desired location
    """
    target_heading: float
    target_speed: float