# ant_colony/ant.py
import random

class Ant:
    def __init__(self, items, capacity, pheromones, alpha, beta):
        self.items = items
        self.capacity = capacity
        self.pheromones = pheromones
        self.alpha = alpha  # Influence des phéromones
        self.beta = beta    # Influence de l'heuristique
        self.solution = []
        self.total_weight = 0
        self.total_value = 0

    def select_item(self, available_items):
        """Sélectionne un objet basé sur les phéromones et l'heuristique"""
        if not available_items:
            return None
            
        probabilities = []
        for item in available_items:
            pheromone = self.pheromones[item.id]
            heuristic = item.value / item.weight if item.weight > 0 else 0
            prob = (pheromone ** self.alpha) * (heuristic ** self.beta)
            probabilities.append(prob)

        total_prob = sum(probabilities)
        if total_prob == 0:
            return random.choice(available_items)

        # Normalisation des probabilités
        probabilities = [p / total_prob for p in probabilities]
        return random.choices(available_items, weights=probabilities, k=1)[0]

    def construct_solution(self):
        """Construit une solution complète pour le sac à dos"""
        self.solution = []
        self.total_weight = 0
        self.total_value = 0
        
        available_items = self.items.copy()
        random.shuffle(available_items)

        while available_items:
            # Filtrer les objets qui peuvent encore être ajoutés
            feasible_items = [item for item in available_items 
                            if self.total_weight + item.weight <= self.capacity]
            
            if not feasible_items:
                break
                
            item = self.select_item(feasible_items)
            if item:
                self.solution.append(item)
                self.total_weight += item.weight
                self.total_value += item.value
                available_items.remove(item)
            else:
                break

        return self.solution, self.total_value

    def reset(self):
        """Remet à zéro la fourmi pour une nouvelle construction"""
        self.solution = []
        self.total_weight = 0
        self.total_value = 0