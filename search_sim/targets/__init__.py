"""Targets Module"""

from search_sim.targets.basic_target import BasicTarget
from search_sim.targets.random_target import RandomTarget
from search_sim.targets.evasive_target import EvasiveTarget

__all__ = [
    "BasicTarget",
    "RandomTarget",
    "EvasiveTarget"
]