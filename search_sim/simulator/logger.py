import csv
import os

"""Logger class to generate csv files of all entity positions throughout the simulation."""

class Logger():
    def __init__(self, output_dir, run_name, hazards, x_size, y_size):
        """
        Parameters:
            - output_dir: folder to save the csv files to
            - run_name: some string, such as the yaml filename, to distinguish between runs
            - hazards: list of hazards in the simulation
            - hazard_size: how big to render the hazards in the animations
        """

        sanitized_run_name = os.path.splitext(os.path.basename(run_name))[0]
        os.makedirs(output_dir, exist_ok=True)

        self.agent_file = open(os.path.join(output_dir, f"{sanitized_run_name}_agents.csv"), "w", newline="")
        self.target_file = open(os.path.join(output_dir, f"{sanitized_run_name}_targets.csv"), "w", newline="")

        self.agent_writer = csv.writer(self.agent_file)
        self.target_writer = csv.writer(self.target_file)

        self.agent_writer.writerow(["timestep","entity_id","x","y"])
        self.target_writer.writerow(["timestep","entity_id","x","y"])

        self.write_hazards(output_dir, run_name, hazards, x_size, y_size)

    def write_hazards(self, output_dir, run_name, hazards, x_size, y_size):
        """
        Records hazard positions and types at logger initialization.

        Parameters:
            - output_dir: folder to save the csv file to
            - run_name: some string, such as the yaml filename, to distinguish between runs
            - hazards: list of hazards in the simulation
        """
        sanitized_run_name = os.path.splitext(os.path.basename(run_name))[0]
        with open(os.path.join(output_dir, f"{sanitized_run_name}_hazards.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["entity_id","x","y","type","x_size","y_size"])
            for hazard in hazards:
                x, y = hazard.get_location()
                writer.writerow([hazard.get_id(), x, y, hazard.get_type().value, x_size, y_size])

    def log_step(self, timestep, agents, targets, flush_frequency=10):
        """
        Writes agent and target positions at each timestep.

        Parameters:
            - timestep: an integer, i.e. 0, 1, 2...
            - agents: a list of all agents in the simulation
            - targets: a list of all targets in the simulation
            - flush_frequency: how often to flush the write buffer. Defaults to 10.
        """
        for agent in agents:
            x,y = agent.get_location()
            self.agent_writer.writerow([timestep, agent.get_id(), x, y])
        for target in targets:
            x,y = target.get_location()
            self.target_writer.writerow([timestep, target.get_id(), x, y])

        if timestep % flush_frequency == 0:
            self.agent_file.flush()
            self.target_file.flush()
    
    def close(self):
        """
        Closes open files.
        """

        self.agent_file.close()
        self.target_file.close()