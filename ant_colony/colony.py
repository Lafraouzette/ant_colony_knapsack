# ant_colony/colony.py
from .ant import Ant
from .pheromone import initialize_pheromones, update_pheromones, get_pheromone_stats

class Colony:
    def __init__(self, problem, alpha=1, beta=2, evaporation=0.5, num_ants=30, iterations=100):
        self.problem = problem
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.num_ants = num_ants
        self.iterations = iterations
        self.pheromones = initialize_pheromones(problem.items)
        self.best_solution = None
        self.best_value = 0
        self.history = []
        self.iteration_stats = []

    def run(self):
        """Exécute l'algorithme de colonie de fourmis"""
        print(f"Démarrage de l'algorithme ACO...")
        print(f"Paramètres: α={self.alpha}, β={self.beta}, évaporation={self.evaporation}")
        print(f"Nombre de fourmis: {self.num_ants}, Itérations: {self.iterations}")
        print(f"Capacité du sac: {self.problem.capacity}")
        print("-" * 60)

        for iteration in range(self.iterations):
            all_solutions = []
            iteration_best_value = 0

            # Chaque fourmi construit une solution
            for _ in range(self.num_ants):
                ant = Ant(self.problem.items, self.problem.capacity, 
                         self.pheromones, self.alpha, self.beta)
                solution, value = ant.construct_solution()
                all_solutions.append((solution, value))

                # Mise à jour de la meilleure solution de l'itération
                if value > iteration_best_value:
                    iteration_best_value = value

                # Mise à jour de la meilleure solution globale
                if value > self.best_value:
                    self.best_solution = solution
                    self.best_value = value

            # Mise à jour des phéromones
            update_pheromones(self.pheromones, all_solutions, self.evaporation,
                            self.best_solution, self.best_value)

            # Enregistrement de l'historique
            self.history.append(self.best_value)
            
            # Statistiques de l'itération
            avg_value = sum(value for _, value in all_solutions) / len(all_solutions)
            self.iteration_stats.append({
                'iteration': iteration + 1,
                'best_value': self.best_value,
                'iteration_best': iteration_best_value,
                'average_value': avg_value
            })

            # Affichage périodique des résultats
            if (iteration + 1) % 20 == 0 or iteration == 0:
                pheromone_stats = get_pheromone_stats(self.pheromones)
                print(f"Itération {iteration + 1:3d}: "
                      f"Meilleure={self.best_value:6.1f}, "
                      f"Moyenne={avg_value:6.1f}, "
                      f"Phéromones(min={pheromone_stats['min']:.2f}, "
                      f"max={pheromone_stats['max']:.2f})")

        return self.best_solution, self.best_value, self.history

    def get_convergence_info(self):
        """Retourne des informations sur la convergence de l'algorithme"""
        if not self.history:
            return None
            
        improvements = []
        for i in range(1, len(self.history)):
            if self.history[i] > self.history[i-1]:
                improvements.append(i)
        
        return {
            'total_iterations': len(self.history),
            'final_value': self.history[-1],
            'improvements_count': len(improvements),
            'improvement_iterations': improvements,
            'convergence_iteration': improvements[-1] if improvements else 0
        }