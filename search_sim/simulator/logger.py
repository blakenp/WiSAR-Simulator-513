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
            - x_size, y_size: world dimensions for hazard scaling
        """

        sanitized_run_name = os.path.splitext(os.path.basename(run_name))[0]
        os.makedirs(output_dir, exist_ok=True)

        self.agent_file = open(os.path.join(output_dir, f"{sanitized_run_name}_agents.csv"), "w", newline="")
        self.target_file = open(os.path.join(output_dir, f"{sanitized_run_name}_targets.csv"), "w", newline="")
        
        self.voronoi_file = open(os.path.join(output_dir, f"{sanitized_run_name}_voronoi.csv"), "w", newline="")

        self.agent_writer = csv.writer(self.agent_file)
        self.target_writer = csv.writer(self.target_file)
        self.voronoi_writer = csv.writer(self.voronoi_file)

        self.agent_writer.writerow(["timestep", "entity_id", "x", "y"])
        self.target_writer.writerow(["timestep", "entity_id", "x", "y"])
        
        self.voronoi_writer.writerow(["timestep", "sample_id", "x1", "y1", "x2", "y2"])

        self.write_hazards(output_dir, run_name, hazards, x_size, y_size)

    def write_hazards(self, output_dir, run_name, hazards, x_size, y_size):
        """Records hazard positions and types at logger initialization."""
        sanitized_run_name = os.path.splitext(os.path.basename(run_name))[0]
        with open(os.path.join(output_dir, f"{sanitized_run_name}_hazards.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["entity_id", "x", "y", "type", "x_size", "y_size"])
            for hazard in hazards:
                x, y = hazard.get_location()
                writer.writerow([hazard.get_id(), x, y, hazard.get_type().value, x_size, y_size])

    def log_step(self, timestep, agents, targets, flush_frequency=10):
        """Writes agent and target positions at each timestep."""
        for agent in agents:
            x, y = agent.get_location()
            self.agent_writer.writerow([timestep, agent.get_id(), x, y])
            
        for target in targets:
            x, y = target.get_location()
            self.target_writer.writerow([timestep, target.get_id(), x, y])

        if timestep % flush_frequency == 0:
            self.agent_file.flush()
            self.target_file.flush()

    def log_voronoi_ridges(self, timestep, ridges_by_sample, flush_frequency=10):
        """
        Writes the topological ridge segments for a specific timestep.
        
        Parameters:
            - timestep: current simulation step
            - ridges_by_sample: List[List[Tuple[Point, Point]]] 
              Outer list represents MCMC samples, inner list represents segments.
        """
        for sample_id, ridges in enumerate(ridges_by_sample):
            for (v1, v2) in ridges:
                self.voronoi_writer.writerow([
                    timestep, 
                    sample_id, 
                    v1[0], 
                    v1[1], 
                    v2[0], 
                    v2[1]
                ])

        if timestep % flush_frequency == 0:
            self.voronoi_file.flush()
    
    def close(self):
        """Closes all open file handles."""
        self.agent_file.close()
        self.target_file.close()
        self.voronoi_file.close()