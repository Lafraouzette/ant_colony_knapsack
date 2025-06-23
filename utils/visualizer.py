# utils/visualizer.py
import matplotlib.pyplot as plt
import numpy as np

def plot_convergence(history, title="Évolution de la meilleure solution (convergence ACO)"):
    """Affiche la courbe de convergence de l'algorithme"""
    plt.figure(figsize=(10, 6))
    plt.plot(history, 'b-', linewidth=2, label="Meilleure valeur")
    plt.xlabel("Itération")
    plt.ylabel("Valeur du sac")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_comparison(histories, labels, title="Comparaison des algorithmes"):
    """Compare plusieurs exécutions ou algorithmes"""
    plt.figure(figsize=(12, 6))
    
    colors = ['b-', 'r-', 'g-', 'm-', 'c-']
    for i, (history, label) in enumerate(zip(histories, labels)):
        plt.plot(history, colors[i % len(colors)], linewidth=2, label=label)
    
    plt.xlabel("Itération")
    plt.ylabel("Valeur du sac")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_solution_distribution(iteration_stats):
    """Affiche la distribution des solutions par itération"""
    iterations = [stat['iteration'] for stat in iteration_stats]
    best_values = [stat['best_value'] for stat in iteration_stats]
    avg_values = [stat['average_value'] for stat in iteration_stats]
    
    plt.figure(figsize=(12, 6))
    plt.plot(iterations, best_values, 'b-', linewidth=2, label="Meilleure solution")
    plt.plot(iterations, avg_values, 'r--', linewidth=2, label="Solution moyenne")
    plt.fill_between(iterations, best_values, avg_values, alpha=0.3)
    
    plt.xlabel("Itération")
    plt.ylabel("Valeur")
    plt.title("Distribution des solutions par itération")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_pheromone_levels(pheromones, items):
    """Visualise les niveaux de phéromones"""
    item_ids = [item.id for item in items]
    pheromone_levels = [pheromones[item.id] for item in items]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(item_ids, pheromone_levels)
    plt.xlabel("ID des objets")
    plt.ylabel("Niveau de phéromone")
    plt.title("Niveaux de phéromones par objet")
    
    # Colorer selon le niveau
    max_pheromone = max(pheromone_levels)
    for bar, level in zip(bars, pheromone_levels):
        bar.set_color(plt.cm.viridis(level / max_pheromone))
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def save_results(results, filename="results.png"):
    """Sauvegarde les résultats dans un fichier"""
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Résultats sauvegardés dans {filename}")