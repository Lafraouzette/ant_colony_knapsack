# ant_colony/__init__.py
from .ant import Ant
from .colony import Colony
from .pheromone import initialize_pheromones, update_pheromones

__all__ = ['Ant', 'Colony', 'initialize_pheromones', 'update_pheromones']