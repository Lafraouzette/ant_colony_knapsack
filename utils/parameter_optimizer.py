"""
Optimisation automatique des paramètres ACO
Utilise différentes stratégies pour trouver les meilleurs paramètres
"""

import random
import numpy as np
from typing import Dict, List, Tuple, Any
import time
from concurrent.futures import ThreadPoolExecutor
import json
import os

class ParameterOptimizer:
    def __init__(self, problem, base_iterations=50, optimization_budget=20):
        self.problem = problem
        self.base_iterations = base_iterations
        self.optimization_budget = optimization_budget
        self.best_params = None
        self.best_score = 0
        self.optimization_history = []
        
        # Plages de recherche pour chaque paramètre
        self.param_ranges = {
            'alpha': (0.1, 3.0),
            'beta': (0.1, 5.0),
            'evaporation': (0.1, 0.9),
            'num_ants': (10, 50),
        }
        
        # Paramètres fixes
        self.fixed_params = {
            'iterations': self.base_iterations
        }

    def random_search(self, n_trials=10) -> Dict[str, Any]:
        """Recherche aléatoire dans l'espace des paramètres"""
        print(f"🔍 Recherche aléatoire avec {n_trials} essais...")
        
        best_params = None
        best_score = 0
        
        for trial in range(n_trials):
            # Génération aléatoire des paramètres
            params = self._generate_random_params()
            
            # Évaluation
            score = self._evaluate_parameters(params)
            
            print(f"  Essai {trial+1}/{n_trials}: Score = {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_params = params.copy()
                
            self.optimization_history.append({
                'method': 'random_search',
                'trial': trial,
                'params': params.copy(),
                'score': score
            })
        
        return best_params, best_score

    def grid_search(self, resolution=3) -> Dict[str, Any]:
        """Recherche par grille avec résolution donnée"""
        print(f"📊 Recherche par grille (résolution {resolution})...")
        
        # Génération de la grille
        param_grids = {}
        for param, (min_val, max_val) in self.param_ranges.items():
            if param == 'num_ants':
                param_grids[param] = [int(x) for x in np.linspace(min_val, max_val, resolution)]
            else:
                param_grids[param] = list(np.linspace(min_val, max_val, resolution))
        
        best_params = None
        best_score = 0
        total_combinations = resolution ** len(param_grids)
        
        print(f"  Total de combinaisons: {total_combinations}")
        
        combination = 0
        for alpha in param_grids['alpha']:
            for beta in param_grids['beta']:
                for evaporation in param_grids['evaporation']:
                    for num_ants in param_grids['num_ants']:
                        combination += 1
                        
                        params = {
                            'alpha': alpha,
                            'beta': beta,
                            'evaporation': evaporation,
                            'num_ants': num_ants,
                            **self.fixed_params
                        }
                        
                        score = self._evaluate_parameters(params)
                        
                        if combination % max(1, total_combinations // 10) == 0:
                            print(f"  Progression: {combination}/{total_combinations} ({100*combination/total_combinations:.1f}%)")
                        
                        if score > best_score:
                            best_score = score
                            best_params = params.copy()
                            
                        self.optimization_history.append({
                            'method': 'grid_search',
                            'combination': combination,
                            'params': params.copy(),
                            'score': score
                        })
        
        return best_params, best_score

    def bayesian_optimization(self, n_trials=15) -> Dict[str, Any]:
        """Optimisation bayésienne simplifiée (acquisition par amélioration attendue)"""
        print(f"🧠 Optimisation bayésienne avec {n_trials} essais...")
        
        # Initialisation avec quelques points aléatoires
        n_initial = min(5, n_trials // 3)
        evaluated_params = []
        evaluated_scores = []
        
        for i in range(n_initial):
            params = self._generate_random_params()
            score = self._evaluate_parameters(params)
            evaluated_params.append(params)
            evaluated_scores.append(score)
            
            print(f"  Initialisation {i+1}/{n_initial}: Score = {score:.2f}")
        
        # Optimisation bayésienne simplifiée
        for trial in range(n_initial, n_trials):
            # Sélection du prochain point par acquisition
            candidate_params = self._select_next_candidate(evaluated_params, evaluated_scores)
            
            # Évaluation
            score = self._evaluate_parameters(candidate_params)
            evaluated_params.append(candidate_params)
            evaluated_scores.append(score)
            
            print(f"  Essai {trial+1}/{n_trials}: Score = {score:.2f}")
            
            self.optimization_history.append({
                'method': 'bayesian',
                'trial': trial,
                'params': candidate_params.copy(),
                'score': score
            })
        
        # Retour du meilleur
        best_idx = np.argmax(evaluated_scores)
        return evaluated_params[best_idx], evaluated_scores[best_idx]

    def adaptive_search(self, n_trials=20) -> Dict[str, Any]:
        """Recherche adaptative qui ajuste la stratégie selon les résultats"""
        print(f"🎯 Recherche adaptative avec {n_trials} essais...")
        
        best_params = None
        best_score = 0
        
        # Phase 1: Exploration large
        exploration_trials = n_trials // 2
        for trial in range(exploration_trials):
            params = self._generate_random_params()
            score = self._evaluate_parameters(params)
            
            if score > best_score:
                best_score = score
                best_params = params.copy()
            
            print(f"  Phase exploration {trial+1}/{exploration_trials}: Score = {score:.2f}")
        
        # Phase 2: Exploitation autour du meilleur
        if best_params:
            exploitation_trials = n_trials - exploration_trials
            for trial in range(exploitation_trials):
                # Perturbation autour du meilleur
                params = self._perturb_params(best_params, intensity=0.2)
                score = self._evaluate_parameters(params)
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                
                print(f"  Phase exploitation {trial+1}/{exploitation_trials}: Score = {score:.2f}")
                
                self.optimization_history.append({
                    'method': 'adaptive',
                    'phase': 'exploitation',
                    'trial': trial,
                    'params': params.copy(),
                    'score': score
                })
        
        return best_params, best_score

    def optimize(self, method='adaptive') -> Dict[str, Any]:
        """Lance l'optimisation avec la méthode choisie"""
        start_time = time.time()
        
        print(f"🚀 Début de l'optimisation des paramètres (méthode: {method})")
        print(f"⚙️  Problème: {len(self.problem.items)} objets, capacité {self.problem.capacity}")
        print("=" * 60)
        
        if method == 'random':
            best_params, best_score = self.random_search(self.optimization_budget)
        elif method == 'grid':
            resolution = max(2, int(self.optimization_budget ** (1/4)))  # Racine 4ème
            best_params, best_score = self.grid_search(resolution)
        elif method == 'bayesian':
            best_params, best_score = self.bayesian_optimization(self.optimization_budget)
        elif method == 'adaptive':
            best_params, best_score = self.adaptive_search(self.optimization_budget)
        else:
            raise ValueError(f"Méthode inconnue: {method}")
        
        optimization_time = time.time() - start_time
        
        print("=" * 60)
        print(f"✅ Optimisation terminée en {optimization_time:.2f}s")
        print(f"🏆 Meilleur score: {best_score:.2f}")
        print(f"🔧 Meilleurs paramètres:")
        for param, value in best_params.items():
            print(f"    {param}: {value}")
        
        self.best_params = best_params
        self.best_score = best_score
        
        return best_params

    def _generate_random_params(self) -> Dict[str, Any]:
        """Génère un ensemble aléatoire de paramètres"""
        params = {}
        for param, (min_val, max_val) in self.param_ranges.items():
            if param == 'num_ants':
                params[param] = random.randint(int(min_val), int(max_val))
            else:
                params[param] = random.uniform(min_val, max_val)
        
        params.update(self.fixed_params)
        return params

    def _evaluate_parameters(self, params: Dict[str, Any]) -> float:
        """Évalue un ensemble de paramètres"""
        from ant_colony.colony import Colony
        
        # Création de la colonie avec les paramètres
        colony = Colony(
            problem=self.problem,
            alpha=params['alpha'],
            beta=params['beta'],
            evaporation=params['evaporation'],
            num_ants=params['num_ants'],
            iterations=params['iterations']
        )
        
        try:
            # Exécution silencieuse
            best_solution, best_value, _ = colony.run()
            return best_value if best_value else 0
        except Exception as e:
            print(f"Erreur lors de l'évaluation: {e}")
            return 0

    def _select_next_candidate(self, evaluated_params: List[Dict], evaluated_scores: List[float]) -> Dict[str, Any]:
        """Sélectionne le prochain candidat pour l'optimisation bayésienne"""
        # Implémentation simplifiée: génère plusieurs candidats et choisit celui avec le meilleur potentiel
        n_candidates = 20
        candidates = [self._generate_random_params() for _ in range(n_candidates)]
        
        # Calcul d'un score d'acquisition simplifié
        best_candidate = None
        best_acquisition = -float('inf')
        
        current_best = max(evaluated_scores) if evaluated_scores else 0
        
        for candidate in candidates:
            # Distance aux points déjà évalués (pour favoriser l'exploration)
            min_distance = float('inf')
            for eval_params in evaluated_params:
                distance = self._param_distance(candidate, eval_params)
                min_distance = min(min_distance, distance)
            
            # Score d'acquisition = potentiel d'amélioration + exploration
            acquisition = min_distance * 0.5  # Favorise l'exploration
            
            if acquisition > best_acquisition:
                best_acquisition = acquisition
                best_candidate = candidate
        
        return best_candidate

    def _param_distance(self, params1: Dict, params2: Dict) -> float:
        """Calcule la distance entre deux ensembles de paramètres"""
        distance = 0
        for param in self.param_ranges:
            if param in params1 and param in params2:
                range_size = self.param_ranges[param][1] - self.param_ranges[param][0]
                normalized_diff = abs(params1[param] - params2[param]) / range_size
                distance += normalized_diff ** 2
        return distance ** 0.5

    def _perturb_params(self, base_params: Dict[str, Any], intensity: float = 0.1) -> Dict[str, Any]:
        """Applique une perturbation aux paramètres"""
        perturbed = base_params.copy()
        
        for param, (min_val, max_val) in self.param_ranges.items():
            if param in perturbed:
                range_size = max_val - min_val
                perturbation = random.gauss(0, intensity * range_size)
                
                new_value = perturbed[param] + perturbation
                new_value = max(min_val, min(max_val, new_value))
                
                if param == 'num_ants':
                    new_value = int(round(new_value))
                
                perturbed[param] = new_value
        
        return perturbed

    def save_optimization_results(self, filename: str = "optimization_results.json"):
        """Sauvegarde les résultats d'optimisation"""
        results = {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'optimization_history': self.optimization_history,
            'param_ranges': self.param_ranges,
            'problem_info': {
                'num_items': len(self.problem.items),
                'capacity': self.problem.capacity
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés dans {filename}")

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'optimisation"""
        if not self.optimization_history:
            return {}
        
        scores = [entry['score'] for entry in self.optimization_history]
        methods = [entry.get('method', 'unknown') for entry in self.optimization_history]
        
        return {
            'total_evaluations': len(self.optimization_history),
            'best_score': max(scores),
            'worst_score': min(scores),
            'average_score': sum(scores) / len(scores),
            'methods_used': list(set(methods)),
            'improvement': max(scores) - min(scores) if scores else 0
        }