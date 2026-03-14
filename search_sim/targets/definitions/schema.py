from dataclasses import dataclass
from enum import Enum

class TargetType(Enum):
    """Types of targets we want to simulate"""

    BASIC_TARGET = "basic_target"

@dataclass(frozen=True)
class TargetState:
    """Immutable state of a target.

    Attributes:
        target_id: Unique identifier for target.
        x: X position in grid cells.
        y: Y position in grid cells.
        value: Value of the target (e.g. importance, reward).
    """

    id: str
    x: float
    y: float
    value: float