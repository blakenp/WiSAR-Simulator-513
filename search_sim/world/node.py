from search_sim.targets.definitions import Target
from search_sim.agents.definitions import Agent

"""Basic node class to keep track of entities in the environment"""

class Node():
    def __init__(
            self,
            population: set = {}  # each node has a set which will contain all of the entities
            ) -> None:
        
        self.population = population



    # methods to check for specific entity types

    def has_target(self) -> bool:
        
        hasTarget = False

        for entity in self.population:
            if type(entity) == Target:
                hasTarget = True
        
        return hasTarget
    
    def has_agent(self) -> bool:
        
        hasAgent = False

        for entity in self.population:
            if type(entity) == Agent:
                hasAgent = True
        
        return hasAgent
    
    def has_hazard(self) -> bool:

        hasHazard = False

        # for entity in self.population:  # uncomment this section when Hazards are implemented
        #     if type(entity) == Hazard:
        #         hasHazard = True

        return hasHazard
    
    

    # basic getter and setter methods

    def get_population(self):
        return self.population

    def update_population(self,newPopulation):
        self.population = newPopulation

    def add(self,newEntity):
        self.population.add(newEntity)

    def remove(self,entity):
        self.population.remove(entity)