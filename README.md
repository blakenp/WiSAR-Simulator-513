# WiSAR-Simulator-513

## How To Run
As of now, we treat each directory as its own module so to run a simulation, you simply run the following command from the root directory of the codebase:

```bash
python -m search_sim example_config.yaml
```

The results of the simulation will be saved in the finished_runs directory as e.g. example_config_agents.csv, example_config_targets.csv, and example_config_hazards.csv.

## How to generate animations

From the root directory, run

```bash
python animate.py --agents [config_name]_agents.csv --targets [config_name]_targets.csv --hazards [config_name]_hazards.csv --output [filename].gif
```

The animate script assumes the simulation CSVs are in the finished_runs directory; if they aren't, it won't work.

You can optionally specify the frames per second of the animation with the ```bash --fps``` flag, and you can specify the time delay between frames with the ```bash --interval``` flag.