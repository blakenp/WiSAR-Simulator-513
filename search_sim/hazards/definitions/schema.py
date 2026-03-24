from enum import Enum
from dataclasses import dataclass

class HazardType(Enum):
    """Types of hazards we want to simulate"""

    STANDING_WATER = "standing_water"
    RUNNING_WATER = "running_water"
    TREE = "tree"
    UNDERGROWTH = "undergrowth"
    BOULDER = "boulder"

@dataclass(frozen=True)
class HazardState:
    """Immutable state of a hazard.

    Attributes:
        hazard_id: Unique identifier for hazard.
        x: X position in grid cells.
        y: Y position in grid cells.
        type: type of hazard.
    """

    id: str
    x: float
    y: float
    type: HazardType