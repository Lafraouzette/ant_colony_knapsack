# config.py
"""
Configuration des paramètres pour l'algorithme ACO
"""

# Paramètres de l'algorithme ACO
ALPHA = 1.0             # Influence des phéromones (exploitation)
BETA = 2.0              # Influence de l'heuristique (exploration)
EVAPORATION = 0.5       # Taux d'évaporation des phéromones (0-1)
NUM_ANTS = 30           # Nombre de fourmis par itération
NUM_ITERATIONS = 100    # Nombre total d'itérations

# Paramètres du problème
KNAPSACK_CAPACITY = 50  # Capacité maximale du sac à dos
DATA_FILE = "data/items.csv"  # Fichier contenant les objets

# Paramètres d'affichage
SHOW_PROGRESS = True    # Afficher le progrès pendant l'exécution
PLOT_RESULTS = True     # Afficher les graphiques des résultats
SAVE_RESULTS = False    # Sauvegarder les résultats dans un fichier

# Paramètres avancés
MIN_PHEROMONE = 0.01    # Niveau minimum de phéromone
MAX_PHEROMONE = 10.0    # Niveau maximum de phéromone
ELITE_FACTOR = 0.1      # Facteur de renforcement élitiste

# Configurations prédéfinies
CONFIGS = {
    'exploitation': {
        'ALPHA': 2.0,
        'BETA': 1.0,
        'EVAPORATION': 0.3,
        'description': 'Favorise l\'exploitation des bonnes solutions'
    },
    'exploration': {
        'ALPHA': 0.5,
        'BETA': 3.0,
        'EVAPORATION': 0.7,
        'description': 'Favorise l\'exploration de nouvelles solutions'
    },
    'equilibre': {
        'ALPHA': 1.0,
        'BETA': 2.0,
        'EVAPORATION': 0.5,
        'description': 'Équilibre entre exploitation et exploration'
    }
}

def get_config(config_name='equilibre'):
    """Retourne une configuration prédéfinie"""
    if config_name in CONFIGS:
        return CONFIGS[config_name]
    else:
        print(f"Configuration '{config_name}' non trouvée. Utilisation de 'equilibre'.")
        return CONFIGS['equilibre']

def print_config():
    """Affiche la configuration actuelle"""
    print("Configuration ACO actuelle:")
    print(f"  ALPHA (phéromones): {ALPHA}")
    print(f"  BETA (heuristique): {BETA}")
    print(f"  EVAPORATION: {EVAPORATION}")
    print(f"  Nombre de fourmis: {NUM_ANTS}")
    print(f"  Nombre d'itérations: {NUM_ITERATIONS}")
    print(f"  Capacité du sac: {KNAPSACK_CAPACITY}")