from pathlib import Path
from search_sim.simulator.definitions.schema import SimulatorState, SimulatorConfig, Timekeeper
from search_sim.agents.definitions.schema import AgentState
import search_sim.agents.factories.agent_factory as agent_factory
from search_sim.targets.definitions.schema import TargetState
from search_sim.simulator.logger import Logger
from search_sim.utils import get_nearby_entities
import math

class Simulator:
    """Main simulation engine.
    
    Orchestrates the simulation loop, advancing time, updating agent states,
    and publishing events. Maintains simulation state as immutable snapshots.
    """

    def __init__(
        self, 
        config: SimulatorConfig,
        initial_state: SimulatorState,
        run_path: str
    ) -> None:
        self._state = initial_state
        self._config = config
        self.is_running = False

        """Initialize the logger and log initial positions of entities."""
        agents = initial_state.agents
        targets = initial_state.targets
        hazards = initial_state.hazards
        size = (self._state.environment.x_length + self._state.environment.y_length)/2

        package_root = Path(__file__).resolve().parent.parent
        output_dir = package_root / "finished_runs"
        self.logger = Logger(str(output_dir), run_path, hazards, size)
        self.logger.log_step(self._state.timekeeper.steps(), agents, targets)
        
        self.initialize()

    def get_state(self) -> SimulatorState:
        """Get current simulation state."""
        return self._state

    def get_timekeeper(self) -> Timekeeper:
        """Get current timekeeper."""
        return self._state.timekeeper

    def initialize(self) -> None:
        self.is_running = True

    def step(self) -> None:
        """Advance the simulation by one time step."""
        current_state = self.get_state()
        current_agents = current_state.agents
        current_targets = current_state.targets
        current_hazards = current_state.hazards
        dt = self._config.step_time_seconds

        agent_actions = {agent.get_id(): agent.get_desired_action() for agent in current_agents}
        
        for agent in current_agents:
            action = agent_actions[agent.get_id()]
            curr_state = agent._state
            
            rad = math.radians(action.target_heading)
            distance = action.target_speed * dt
            
            new_x = curr_state.x + (math.cos(rad) * distance)
            new_y = curr_state.y + (math.sin(rad) * distance)
            
            updated_agent_state = AgentState(
                id=curr_state.id,
                type=curr_state.type,
                x=new_x,
                y=new_y,
                heading=action.target_heading,
                battery_percent=curr_state.battery_percent - (0.01 * dt),
                speed_mps=action.target_speed,
                is_active=curr_state.is_active
            )
            agent.update_state(updated_agent_state)

        """Targets need to know the timestep so they know how far they can go in a given action."""
        target_actions = {target.get_id(): target.get_desired_action(dt) for target in current_targets}

        for target in current_targets:
            action = target_actions[target.get_id()]
            curr_state = target._state
            
            rad = math.radians(action.target_heading)
            distance = action.target_speed * dt
            
            new_x = curr_state.x + (math.cos(rad) * distance)
            new_y = curr_state.y + (math.sin(rad) * distance)

            """Check for agents, other targets, and hazards within some radius of the target's new position."""
            new_agents, new_targets, new_hazards = get_nearby_entities(target.get_id(),new_x, new_y, curr_state.awareness_radius, 
                                                                              current_agents, current_targets, current_hazards)
            
            updated_target_state = TargetState(
                id=curr_state.id,
                type=curr_state.type,
                x=new_x,
                y=new_y,
                value = curr_state.value,
                traversable_hazards=curr_state.traversable_hazards,
                heading=action.target_heading,
                speed_mps=action.target_speed,
                max_speed = curr_state.max_speed,
                awareness_radius=curr_state.awareness_radius,
                nearby_agents=new_agents,
                nearby_targets=new_targets,
                nearby_hazards=new_hazards,
            )
            target.update_state(updated_target_state)

        if self.check_target_reached(current_agents, current_targets):
            print("Target reached! Stopping simulation.")
            self.stop()

        # Advance State Snapshot
        self._state = SimulatorState(
            timekeeper=current_state.timekeeper.advance(),
            environment=current_state.environment,
            agents=current_agents,
            targets=current_targets,
            hazards=current_state.hazards
        )

        """Log the step we just completed."""
        self.logger.log_step(self._state.timekeeper.steps(), self._state.agents, self._state.targets)

    def check_target_reached(self, agents, targets) -> bool:
        """Determines if any agent has entered a cell containing a target."""
        env = self._state.environment
        
        for agent in agents:
            agent_indices = env.get_indices(agent.get_location())
            
            for target in targets:
                target_indices = env.get_indices(target.get_location())
                
                if agent_indices == target_indices:
                    return True
        return False

    def run(self) -> None:
        """Run the simulation loop until time limit or stopped."""
        self.initialize()
        
        while self.get_timekeeper().elapsed_seconds() < self._config.time_limit_seconds:
            if not self.is_running:
                break
            self.step()

    def stop(self) -> None:
        """Stop the simulation."""
        self.is_running = False