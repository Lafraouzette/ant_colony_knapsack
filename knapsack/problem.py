# knapsack/problem.py
import csv
from .item import Item

class KnapsackProblem:
    def __init__(self, file_path, capacity):
        self.items = self.load_items(file_path)
        self.capacity = capacity

    def load_items(self, file_path):
        """Charge les objets depuis un fichier CSV"""
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item = Item(int(row['id']), float(row['weight']), float(row['value']))
                    items.append(item)
        except FileNotFoundError:
            print(f"Erreur: Le fichier {file_path} n'a pas été trouvé.")
            return []
        except Exception as e:
            print(f"Erreur lors du chargement du fichier: {e}")
            return []
        return items

    def evaluate(self, solution):
        """Évalue une solution et retourne sa valeur (0 si invalide)"""
        total_weight = sum(item.weight for item in solution)
        total_value = sum(item.value for item in solution)
        if total_weight > self.capacity:
            return 0  # Solution invalide
        return total_value

    def get_solution_info(self, solution):
        """Retourne les informations détaillées d'une solution"""
        total_weight = sum(item.weight for item in solution)
        total_value = sum(item.value for item in solution)
        return total_weight, total_value

    def is_valid_solution(self, solution):
        """Vérifie si une solution respecte la contrainte de capacité"""
        total_weight = sum(item.weight for item in solution)
        return total_weight <= self.capacity

    def print_problem_info(self):
        """Affiche les informations du problème"""
        print(f"Problème du sac à dos:")
        print(f"- Capacité: {self.capacity}")
        print(f"- Nombre d'objets: {len(self.items)}")
        print(f"- Objets disponibles:")
        for item in self.items:
            ratio = item.value / item.weight if item.weight > 0 else 0
            print(f"  {item} (ratio: {ratio:.2f})")