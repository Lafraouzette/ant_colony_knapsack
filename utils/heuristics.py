# utils/heuristics.py

def value_weight_ratio(item):
    """Calcule le ratio valeur/poids d'un objet"""
    return item.value / item.weight if item.weight > 0 else 0

def greedy_solution(items, capacity):
    """Génère une solution gloutonne basée sur le ratio valeur/poids"""
    # Trier les objets par ratio décroissant
    sorted_items = sorted(items, key=value_weight_ratio, reverse=True)
    
    solution = []
    total_weight = 0
    total_value = 0
    
    for item in sorted_items:
        if total_weight + item.weight <= capacity:
            solution.append(item)
            total_weight += item.weight
            total_value += item.value
    
    return solution, total_value

def calculate_efficiency(items):
    """Calcule l'efficacité (ratio valeur/poids) de chaque objet"""
    return {item.id: value_weight_ratio(item) for item in items}

def get_best_items_by_ratio(items, n=5):
    """Retourne les n meilleurs objets selon leur ratio valeur/poids"""
    return sorted(items, key=value_weight_ratio, reverse=True)[:n]