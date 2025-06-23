"""
Point d'entrée principal pour l'optimisation du sac à dos par colonie de fourmis
Auteur: Votre nom
Date: 2025
"""

import os
import sys
import argparse
from knapsack import KnapsackProblem
from ant_colony import Colony
from utils import plot_convergence, greedy_solution, value_weight_ratio
import config

def print_solution(solution, value, weight, capacity):
    """Affiche les détails d'une solution"""
    print("\n" + "="*60)
    print("SOLUTION TROUVÉE")
    print("="*60)
    print(f"Valeur totale: {value}")
    print(f"Poids total: {weight}/{capacity}")
    print(f"Utilisation: {(weight/capacity)*100:.1f}%")
    print(f"Nombre d'objets sélectionnés: {len(solution)}")
    print("\nObjets dans le sac:")
    
    for item in sorted(solution, key=lambda x: x.id):
        ratio = value_weight_ratio(item)
        print(f"  - Objet {item.id}: poids={item.weight}, valeur={item.value}, ratio={ratio:.2f}")
    
    print("="*60)

def compare_with_greedy(problem):
    """Compare avec la solution gloutonne"""
    greedy_sol, greedy_val = greedy_solution(problem.items, problem.capacity)
    greedy_weight = sum(item.weight for item in greedy_sol)
    
    print("\n" + "-"*60)
    print("COMPARAISON AVEC L'ALGORITHME GLOUTON")
    print("-"*60)
    print(f"Solution gloutonne:")
    print(f"  Valeur: {greedy_val}")
    print(f"  Poids: {greedy_weight}/{problem.capacity}")
    print(f"  Objets: {[item.id for item in greedy_sol]}")
    
    return greedy_val, greedy_weight

def run_interactive_mode():
    """Mode interactif pour configurer les paramètres"""
    print("🔧 MODE INTERACTIF - CONFIGURATION DES PARAMÈTRES")
    print("="*50)
    
    try:
        # Configuration de la capacité du sac
        capacity = input(f"Capacité du sac à dos [{config.KNAPSACK_CAPACITY}]: ")
        if capacity.strip():
            config.KNAPSACK_CAPACITY = int(capacity)
        
        # Configuration du nombre de fourmis
        num_ants = input(f"Nombre de fourmis [{config.NUM_ANTS}]: ")
        if num_ants.strip():
            config.NUM_ANTS = int(num_ants)
        
        # Configuration du nombre d'itérations
        iterations = input(f"Nombre d'itérations [{config.NUM_ITERATIONS}]: ")
        if iterations.strip():
            config.NUM_ITERATIONS = int(iterations)
        
        # Configuration d'alpha
        alpha = input(f"Alpha (importance des phéromones) [{config.ALPHA}]: ")
        if alpha.strip():
            config.ALPHA = float(alpha)
        
        # Configuration de beta
        beta = input(f"Beta (importance heuristique) [{config.BETA}]: ")
        if beta.strip():
            config.BETA = float(beta)
        
        # Configuration de l'évaporation
        evaporation = input(f"Taux d'évaporation [{config.EVAPORATION}]: ")
        if evaporation.strip():
            config.EVAPORATION = float(evaporation)
        
        print("\n✅ Configuration mise à jour!")
        
    except ValueError as e:
        print(f"❌ Erreur de saisie: {e}")
        print("Utilisation des valeurs par défaut.")
    
    except KeyboardInterrupt:
        print("\n🚫 Configuration annulée par l'utilisateur.")
        return False
    
    return True

def print_config_info():
    """Affiche la configuration actuelle"""
    print("⚙️  CONFIGURATION ACTUELLE")
    print("="*40)
    print(f"Fichier de données: {config.DATA_FILE}")
    print(f"Capacité du sac: {config.KNAPSACK_CAPACITY}")
    print(f"Nombre de fourmis: {config.NUM_ANTS}")
    print(f"Nombre d'itérations: {config.NUM_ITERATIONS}")
    print(f"Alpha: {config.ALPHA}")
    print(f"Beta: {config.BETA}")
    print(f"Évaporation: {config.EVAPORATION}")
    print("="*40)

def run_experiment():
    """Exécute l'expérience principale"""
    print("🐜 OPTIMISATION DU SAC À DOS PAR COLONIE DE FOURMIS 🐜")
    print("="*70)
    
    # Vérification du fichier de données
    if not os.path.exists(config.DATA_FILE):
        print(f"❌ Erreur: Le fichier {config.DATA_FILE} n'existe pas!")
        print("Veuillez créer le fichier avec les objets à analyser.")
        print(f"Format attendu: id,weight,value")
        return False
    
    # Initialisation du problème
    try:
        problem = KnapsackProblem(config.DATA_FILE, config.KNAPSACK_CAPACITY)
        if not problem.items:
            print("❌ Aucun objet chargé. Vérifiez le fichier de données.")
            return False
            
        problem.print_problem_info()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du problème: {e}")
        return False
    
    # Comparaison avec la solution gloutonne
    try:
        greedy_value, greedy_weight = compare_with_greedy(problem)
    except Exception as e:
        print(f"⚠️  Erreur lors du calcul de la solution gloutonne: {e}")
        greedy_value, greedy_weight = 0, 0
    
    # Configuration de l'algorithme ACO
    config.print_config()
    
    # Initialisation et exécution de la colonie
    print(f"\n🚀 Démarrage de l'optimisation...")
    
    colony = Colony(
        problem=problem,
        alpha=config.ALPHA,
        beta=config.BETA,
        evaporation=config.EVAPORATION,
        num_ants=config.NUM_ANTS,
        iterations=config.NUM_ITERATIONS
    )
    
    try:
        # Exécution de l'algorithme
        best_solution, best_value, history = colony.run()
        
        if best_solution:
            weight, value = problem.get_solution_info(best_solution)
            print_solution(best_solution, best_value, weight, config.KNAPSACK_CAPACITY)
            
            # Comparaison des performances
            if greedy_value > 0:
                improvement = ((best_value - greedy_value) / greedy_value * 100)
                print(f"\n📊 Amélioration par rapport à la solution gloutonne: {improvement:+.1f}%")
            
            # Affichage du graphique de convergence
            try:
                plot_convergence(history)
                print("📈 Graphique de convergence sauvegardé dans 'convergence.png'")
            except Exception as e:
                print(f"⚠️  Impossible de générer le graphique: {e}")
            
            return True
        else:
            print("❌ Aucune solution trouvée!")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de la colonie: {e}")
        return False

def main():
    """Fonction principale avec gestion des arguments"""
    parser = argparse.ArgumentParser(
        description="Optimisation du sac à dos par colonie de fourmis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py              # Exécution normale
  python main.py -i           # Mode interactif
  python main.py -c           # Afficher la configuration
  python main.py --help       # Afficher cette aide
        """
    )
    
    parser.add_argument('-i', '--interactive', 
                       action='store_true',
                       help='Mode interactif pour configurer les paramètres')
    
    parser.add_argument('-c', '--config', 
                       action='store_true',
                       help='Afficher la configuration actuelle')
    
    args = parser.parse_args()
    
    # Gestion des arguments
    if args.config:
        print_config_info()
        return
    
    if args.interactive:
        if not run_interactive_mode():
            return
    
    # Exécution de l'expérience
    success = run_experiment()
    
    if success:
        print("\n✅ Optimisation terminée avec succès!")
    else:
        print("\n❌ L'optimisation a échoué.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🚫 Programme interrompu par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)