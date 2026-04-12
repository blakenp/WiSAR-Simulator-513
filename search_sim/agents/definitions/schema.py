from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class AgentType(Enum):
    """Types of agents in the simulation."""

    RANDOM_AGENT = "random_agent"
    DIRECT_PATH_FINDER_AGENT = "direct_path_finder_agent"
    VORONOI_BAYES_AGENT = "voronoi_bayes_agent"

@dataclass(frozen=True)
class SensorObservation:
    distance: float
    bearing: float
    noise_sigma: float

@dataclass(frozen=True)
class AgentState:
    """Immutable state of an agent.

    Attributes:
        agent_id: Unique identifier for agent.
        agent_type: Type of agent.
        x: X position in grid cells.
        y: Y position in grid cells.
        traversable_hazards: All hazard types the target can navigate through.
        heading: Heading in degrees (0-360).
        battery_percent: Battery level 0-100 (for UAVs).
        speed_mps: Current speed in meters per second.
        is_active: Whether agent is operational.
    """

    id: str
    type: AgentType
    x: float
    y: float
    traversable_hazards: list[str]
    heading: float
    battery_percent: float
    speed_mps: float
    is_active: bool
    sensor_range: Optional[float] = None
    num_rays: Optional[int] = None
    sensor_noise: Optional[float] = None
    recent_sensor_readings: Optional[List[SensorObservation]] = None
    
@dataclass(frozen=True)
class AgentAction:
    """The 'Intent' of an agent for the next step.
    
    Attributes:
        target_heading: Heading of where the agent wants to move
        target_speed: How fast the agent wants to move to desired location
    """
    target_heading: float
    target_speed: float
