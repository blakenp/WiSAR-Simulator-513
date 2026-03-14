from search_sim.simulator.simulator import Simulator
from search_sim.simulator.definitions.schema import SimulatorConfig, SimulatorState, Timekeeper
from search_sim.world.environment import Environment
from search_sim.world.probability_map import ProbabilityMap
from search_sim.world.nodes.definitions.schema import ProbabilityNode
from search_sim.agents.factories.agent_factory import agent_factory
from search_sim.targets.factories.target_factory import target_factory
from search_sim.agents.definitions.schema import AgentType, AgentState
from search_sim.targets.definitions.schema import TargetState, TargetType

def setup_entities():
    """Helper to instantiate agents and targets using factories."""
    
    target_pos = (8.5, 8.5)
    initial_target_state = TargetState(
        id="target_0",
        x=target_pos[0],
        y=target_pos[1],
        value=100.0
    )

    target = target_factory(
        TargetType.BASIC_TARGET, 
        target_state=initial_target_state
    )

    belief_map = ProbabilityMap(x_length=10, y_length=10, num_x_pts=10, num_y_pts=10)
    goal_node = belief_map.get_node(target_pos)
    goal_node.update_node_data(ProbabilityNode(probability=1.0))

    initial_agent_state = AgentState(
        id="uav_1",
        type=AgentType.DIRECT_PATH_FINDER_AGENT,
        x=1.0, 
        y=1.0,
        heading=0.0,
        battery_percent=100.0,
        speed_mps=1.5,
        is_active=True
    )

    agent = agent_factory(
        AgentType.DIRECT_PATH_FINDER_AGENT,
        initial_state=initial_agent_state,
        initial_map=belief_map
    )

    return [agent], [target]

def main():
    # --- 1. Configuration ---
    config = SimulatorConfig(
        time_limit_seconds=30.0,
        step_time_seconds=0.1
    )

    # --- 2. Instantiate World ---
    agents, targets = setup_entities()
    
    env = Environment(
        entities=agents + targets,
        x_length=10.0,
        y_length=10.0,
        num_x_pts=10,
        num_y_pts=10
    )

    # --- 3. Initial State Snapshot ---
    initial_state = SimulatorState(
        timekeeper=Timekeeper(step=0, time_step_seconds=config.step_time_seconds),
        environment=env,
        agents=agents,
        targets=targets
    )

    # --- 4. Run Simulation ---
    sim = Simulator(config=config, initial_state=initial_state)
    
    print(f"Starting simulation: {config.time_limit_seconds}s limit...")
    sim.run()
    
    # Final Report
    final_pos = agents[0].get_location()
    print(f"Simulation Complete at {sim.get_timekeeper().format_time()}")
    print(f"Agent final position: {final_pos}")

if __name__ == "__main__":
    main()