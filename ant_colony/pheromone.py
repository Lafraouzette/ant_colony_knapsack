# ant_colony/pheromone.py

def initialize_pheromones(items, initial_value=1.0):
    """Initialise les niveaux de phéromones pour tous les objets"""
    return {item.id: initial_value for item in items}

def update_pheromones(pheromones, all_solutions, evaporation_rate, best_solution, best_value):
    """Met à jour les niveaux de phéromones après une itération"""
    
    # Phase d'évaporation
    for item_id in pheromones:
        pheromones[item_id] *= (1 - evaporation_rate)
        # Éviter que les phéromones deviennent trop faibles
        if pheromones[item_id] < 0.01:
            pheromones[item_id] = 0.01
    
    # Renforcement basé sur la qualité des solutions
    for solution, value in all_solutions:
        if value > 0:  # Solution valide
            pheromone_deposit = value / best_value if best_value > 0 else 0
            for item in solution:
                pheromones[item.id] += pheromone_deposit
    
    # Renforcement élitiste pour la meilleure solution
    if best_solution and best_value > 0:
        elite_deposit = best_value * 0.1
        for item in best_solution:
            pheromones[item.id] += elite_deposit

def get_pheromone_stats(pheromones):
    """Retourne des statistiques sur les niveaux de phéromones"""
    values = list(pheromones.values())
    return {
        'min': min(values),
        'max': max(values),
        'avg': sum(values) / len(values)
    }