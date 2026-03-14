from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    """Types of agents in the simulation."""

    RANDOM_AGENT = "random_agent"
    DIRECT_PATH_FINDER_AGENT = "direct_path_finder_agent"

@dataclass(frozen=True)
class AgentState:
    """Immutable state of an agent.

    Attributes:
        agent_id: Unique identifier for agent.
        agent_type: Type of agent.
        x: X position in grid cells.
        y: Y position in grid cells.
        heading: Heading in degrees (0-360).
        battery_percent: Battery level 0-100 (for UAVs).
        speed_mps: Current speed in meters per second.
        is_active: Whether agent is operational.
    """

    id: str
    type: AgentType
    x: float
    y: float
    heading: float
    battery_percent: float
    speed_mps: float
    is_active: bool
    
@dataclass(frozen=True)
class AgentAction:
    """The 'Intent' of an agent for the next step.
    
    Attributes:
        target_heading: Heading of where the agent wants to move
        target_speed: How fast the agent wants to move to desired location
    """
    target_heading: float
    target_speed: float
