# WiSAR-Simulator-513
This codebase's purpose is to create a _Wilderness Search and Rescue_ simulator with configurable scenarios, modeling a dynamic system of an agent searching for a target (that could be static or dynamic as well). We hope to be able to study how to model dynamics as an optimization problem in which we try to optimally choose where to go/search for a target in the face of uncertainty.

The public repository of this codebase can be found [here](https://github.com/blakenp/WiSAR-Simulator-513).

### What This Code Is

This simulator was written as a class project for CS 513 at BYU. As such, it is fairly limited in scope, and therefore in usefulness. Our primary goal in writing the simulator was to gain a deeper understanding of how such a piece of software should be structured, and of some of the harder questions that would need to be answered.

### What This Code Is Not

Complete. We had limited time to complete the project, and were not able to implement all of the features we would have liked. There are also some design decisions we made early on that may not have been the best option; for instance, our implementation of environmental hazards ended up being very fiddly and difficult to work with.

Incompleteness in mind, we did do our best to make the software relatively easy to extend. Everything is written from an object-oriented perspective, with abstract base classes for specific types of search agents or targets to implement. This means that it should be relatively straightforward, if desired, to add an agent which implements some new type of search algorithm.

With all of that said, if you are looking for a robust piece of software to run simulations on, this is probably not it. You might investigate [BYU FROST Lab's ocean search and rescue simulator](https://frostlab.byu.edu/research/HoloOcean-Underwater-Simulator/), for example. Regardless, hopefully our work can provide some insight into how such a simulator might work.

## How To Run
As of now, we treat each directory as its own module so to run a simulation, you simply run the following command from the root directory of the codebase:

```bash
python -m search_sim example_config.yaml
```

In our codebase, we created a `SimulatorConfigParser` that reads in the yaml config files and has a _builder_ layer that acts as an adapter between a user's config file and the codebase data objects we defined here. It builds agents, targets, the environment, belief maps, etc and then instantiates the final `Simulator` object that holds these entities in its state.

The results of the simulation will be saved in the finished_runs directory as e.g. example_config_agents.csv, example_config_targets.csv, and example_config_hazards.csv.

### Generating animations

From the root directory, run

```bash
python animate.py --agents [config_name]_agents.csv --targets [config_name]_targets.csv --hazards [config_name]_hazards.csv --output [filename].gif
```

The animate script assumes the simulation CSVs are in the finished_runs directory; if they aren't, it won't work.

You can optionally specify the frames per second of the animation with the ```--fps``` flag, and you can specify the time delay between frames with the ```--interval``` flag.

## Simulator

The simulator's main responsibility in our codebase is to be the orchestrator of the physics and interaction of entities in our code. Although our agents and targets can make moves, we went with the approach of making it so the functions on targets and agents don't internally update state, but that rather an agent or target has a function that outputs their desired action, and then the simulator reads in the desired action and creates a new state for the entity that is moving and passes that into the entity's update state function. This way, the simulator is in charge of the orchestration of the dynamics of our model of interacting entities, and then entities only indicate their desires rather than having a `move` function or something similar. 

We specifically bundled all updates of agents and targets so that we wouldn't update 1 agent's state in a simulation step before another agent had the opportunity to move so that we weren't creating situations in which an agent would make a decision based on another agent's action in the same step. By bundling all agent and target updates into a single discrete step, we eliminate 'race conditions' where one agent might react to another’s movement within the same frame. This allowed us to more easily construct snapshots of the simulator state at each step of the simulation, and to iteratively handle each entity's dynamics iteratively and synchronously. 

Below, we dive deeper into some more of our strategies for organizing our code and making it flexible for adding different types of targets and agents without having to add or change too many existing files.

## Code structure

We have several modules that work together to simulate the behavior of the entire system. While there are some important differences in how each module is implemented, there are some significant similarities as well. Most instances of a given module maintain a state vector, which contains all the information needed to compute the next step taken by the module. We also have custom types, factory methods, and so forth for each module.

### Agents

We have implemented one agent so far (but hope to finish a 2nd one that will be a Bayesian filtering agent). Here are the differnt agent behaviors we have implemeted:

- direct path finding agents know where the target is from the get go and simply move towards them to attempt to get into the same cell as them and finish the simulation.

The behavior of our direct path agent is simply modeling a [Dubins Vehicle](https://en.wikipedia.org/wiki/Dubins_path), although our agent can have a non-constant velocity. What this means is that our agent is pretty simple in the sense that it has a dynamical function for updating its position ($\dot{x}, \dot{y}$) and that it also has some heading that can be adjusted $\dot{\theta}$ according to the agent's desired behavior.

As for the specific code structure we went with this, we made a generic base class where the generic `AgentState` can be specified in concrete implementations of our interface-like class `Entity`. We made this class as flexible as possible to allow targets and hazards to also have concrete implementations of it, but we also made a more specific `Agent` abstract base class that describes basic agentic behavior we expected to see among all agent types, and so each of our concrete agent class implementations could simply implement both the `Entity[AgentState]` and `Agent` base classes.

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

## Example Simulation Animations

Below are a few example animations of simulations that were run on our software. All of these simulations feature the direct path agent mentioned above, so the agent behavior is not particularly intelligent.

#### Small environment, single evasive target

![Single Target Animation](search_sim/animations/direct_path_test.gif)

A single target running away from a single agent. The agent is faster than the target, and so is able to catch up. In this simulation, the direct path agent's ability to find *a* possible move, even if it's not on the direct line toward the target, is demonstrated.

#### Larger environment, two evasive targets

![Two Target Animation](search_sim/animations/larger_test.gif)

Two targets evading two agents. The agents are unable to cross the river and so get stuck. It's not completely clear why this happens, but it's due to some interplay between the desire to go straight toward the targets, the inability to cross the river, and the ability to find *a* move&mdash;somehow, the end result is that the agents keep stepping away from and then back towards the river indefinitely.

#### Larger environment, two intelligent targets

![Two Smart Target Animation](search_sim/animations/smart_test.gif)

Two targets trying to be found by two agents. The agents are again unable to cross the river for the same reasons as above. The targets' awareness radii are big enough that the target which moves toward the river is able to "see" the agents and attempt to reach them, but the simulation never quite terminates. We believe the target's move scoring algorithm reaches some sort of equilibrium between wanting to move toward the agents and not wanting to be more surrounded by hazards *just* before the simulation would otherwise terminate.
