"""Basic target class"""

from search_sim.targets.definitions.interfaces import Target

class BasicTarget(Target):
    def __init__(self, id, location, value=1):  # default target value is 1
        self.id = id
        self.location = location
        self.value = value

    def get_id(self) -> str:
        return self.id

    def get_location(self) -> tuple[float,float]:
        return self.location

    def get_value(self) -> float:
        return self.value