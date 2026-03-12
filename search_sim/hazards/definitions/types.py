from enum import Enum

class HazardType(Enum):
    """Types of hazards we want to simulate"""

    STANDING_WATER = "standing_water"
    RUNNING_WATER = "running_water"
    TREE = "tree"
    UNDERGROWTH = "undergrowth"
    BOULDER = "boulder"