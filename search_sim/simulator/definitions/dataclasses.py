
from dataclasses import dataclass
from typing import List

from search_sim.agents.definitions.dataclasses import AgentState
from search_sim.agents.definitions.interfaces import Agent
from search_sim.targets.definitions.interfaces import Target
from search_sim.world.environment import Environment


@dataclass(frozen=True)
class SimulatorState:
    """Immutable state snapshot of the simulation.
    
    Attributes:
        timekeeper: Current simulation time.
        environment: Current environment and its state.
        agents: Current agents in simulation.
        targets: Current targets in simulation.
    """

    timekeeper: Timekeeper
    environment: Environment
    agents: List[Agent]
    targets: List[Target]

@dataclass(frozen=True)
class Timekeeper:
    """Immutable timekeeper for tracking simulation time.
    
    Manages simulation step count and can compute elapsed time at any scale.
    """

    step: int = 0
    time_step_seconds: float = 1.0

    def advance(self) -> "Timekeeper":
        return Timekeeper(step=self.step + 1, time_step_seconds=self.time_step_seconds)

    def elapsed_seconds(self) -> float:
        return self.step * self.time_step_seconds

    def elapsed_minutes(self) -> float:
        return self.elapsed_seconds() / 60.0

    def elapsed_hours(self) -> float:
        return self.elapsed_minutes() / 60.0

    def format_time(self) -> str:
        total_seconds: int = int(self.elapsed_seconds())
        hours: int = total_seconds // 3600
        minutes: int = (total_seconds % 3600) // 60
        seconds: int = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
