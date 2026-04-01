# WiSAR-Simulator-513

## How To Run
As of now, we treat each directory as its own module so to run a simulation, you simply run the following command from the root directory of the codebase:

```bash
python -m search_sim example_config.yaml
```

The results of the simulation will be saved in the finished_runs directory as e.g. example_config_agents.csv, example_config_targets.csv, and example_config_hazards.csv.

### Generating animations

From the root directory, run

```bash
python animate.py --agents [config_name]_agents.csv --targets [config_name]_targets.csv --hazards [config_name]_hazards.csv --output [filename].gif
```

The animate script assumes the simulation CSVs are in the finished_runs directory; if they aren't, it won't work.

You can optionally specify the frames per second of the animation with the ```--fps``` flag, and you can specify the time delay between frames with the ```--interval``` flag.

## Code structure

### Targets

We have implemented four target behaviors: static, evasive, random walking, and "intelligent":

- static targets stay stationary, in the position they were initialized in
- evasive targets avoid agents and seek hazards
- random walking targets pick a random direction and a random speed at each timestep
- intelligent targets avoid hazards and move toward agents

Evasive and intelligent targets generate a list of potential actions to take, and score them based on their desired behavior. The highest-scoring action is the one the target ends up taking. Currently, evasive targets place equal weight on avoiding agents and moving towards hazards and intelligent targets place equal weight on moving towards agents and avoiding hazards, but these weights could be adjusted to get slightly different behavior.

### Hazards

We have implemented five hazard types:

- running water
- standing water
- tree
- undergrowth
- boulder

These hazards are functionally identical in that they only store a position; the differences in behavior come from the entities navigating the environment and which hazards they are programmed to be able to navigate. As constructed, we assume a hazard occupies an entire cell in the environment.

### World

The primary structure of this module is a 2D array of nodes. Each node stores a set that contains all of the entities in the cell.