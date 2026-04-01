import argparse
from search_sim.cli.input.simulator_builder import SimulatorBuilder
from search_sim.cli.input.simulator_config_parser import SimulatorConfigParser
from search_sim.simulator.simulator import Simulator

def main(args=None):
    arg_parser = argparse.ArgumentParser(description="Run the Search Simulator.")
    arg_parser.add_argument(
        "config_path", 
        help="Path to the YAML configuration file",
    )
    
    parsed_args = arg_parser.parse_args(args)
    simulator_config_builder = SimulatorBuilder()
    simulator_config_parser = SimulatorConfigParser(config_builder=simulator_config_builder)

    try:
        config, state = simulator_config_parser.parse(parsed_args.config_path)
    except FileNotFoundError:
        print(f"Error: Could not find config file at {parsed_args.config_path}")
        return 1

    sim = Simulator(config, state, parsed_args.config_path)
    
    print(f"Starting simulation using: {parsed_args.config_path}")
    sim.run()
    
    # Final Report
    final_pos = sim.get_state().agents[0].get_location()
    print(f"Simulation Complete at {sim.get_timekeeper().format_time()}")
    print(f"Agent final position: {final_pos}")
    return 0