from search_sim.simulator.definitions.dataclasses import SimulatorState, Timekeeper

class Simulator:
    """Main simulation engine.
    
    Orchestrates the simulation loop, advancing time, updating agent states,
    and publishing events. Maintains simulation state as immutable snapshots.
    """

    def __init__(
        self, 
        time_limit: float, 
        initial_state: SimulatorState
    ) -> None:
        self.state = initial_state
        self.time_limit = time_limit
        self.is_running = False
        
        self.initialize()

    @property
    def state(self) -> SimulatorState:
        """Get current simulation state."""
        return self.state

    @property
    def timekeeper(self) -> Timekeeper:
        """Get current timekeeper."""
        return self.state.timekeeper

    def initialize(self) -> None:
        self.is_running = True

    def step(self) -> None:
        pass

    def run(self) -> None:
        """Run the simulation for a time limit.
        
        Args:
            max_steps: Time limit to run simulator for.
        """
        self.initialize()
        while self.state.timekeeper.elapsed_seconds < self.time_limit:
            if not self.is_running:
                break
            self.step()

    def stop(self) -> None:
        """Stop the simulation."""
        self.is_running = False
