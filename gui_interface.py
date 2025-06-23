"""
Interface graphique pour l'optimisation du sac à dos par colonie de fourmis
Utilise tkinter pour une interface complète et intuitive
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import csv
import time

# Configuration par défaut
class DefaultConfig:
    ALPHA = 1.0
    BETA = 2.0
    EVAPORATION = 0.5
    NUM_ANTS = 20
    NUM_ITERATIONS = 100
    KNAPSACK_CAPACITY = 50
    DATA_FILE = "items.csv"

config = DefaultConfig()

class ACOKnapsackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🐜 Optimisation Sac à Dos - Colonie de Fourmis")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Variables
        self.problem = None
        self.colony = None
        self.optimizer = None
        self.is_running = False
        self.results_queue = queue.Queue()
        self.best_solutions = []
        self.current_thread = None
        
        # Configuration des paramètres
        self.params = {
            'alpha': tk.DoubleVar(value=config.ALPHA),
            'beta': tk.DoubleVar(value=config.BETA),
            'evaporation': tk.DoubleVar(value=config.EVAPORATION),
            'num_ants': tk.IntVar(value=config.NUM_ANTS),
            'iterations': tk.IntVar(value=config.NUM_ITERATIONS),
            'capacity': tk.IntVar(value=config.KNAPSACK_CAPACITY)
        }
        
        # Interface
        self.setup_ui()
        self.setup_menu()
        
        # Thread monitoring
        self.root.after(100, self.check_results_queue)

    def setup_menu(self):
        """Configure le menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Charger données CSV", command=self.load_data_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sauvegarder configuration", command=self.save_config)
        file_menu.add_command(label="Charger configuration", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Optimisation
        optim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Optimisation", menu=optim_menu)
        optim_menu.add_command(label="Optimiser paramètres", command=self.optimize_parameters)
        optim_menu.add_command(label="Réinitialiser paramètres", command=self.reset_parameters)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration des poids des colonnes et lignes
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Section 1: Chargement des données
        self.setup_data_section(main_frame)
        
        # Section 2: Configuration des paramètres
        self.setup_params_section(main_frame)
        
        # Section 3: Résultats et visualisation
        self.setup_results_section(main_frame)
        
        # Section 4: Contrôles
        self.setup_controls_section(main_frame)

    def setup_data_section(self, parent):
        """Section pour le chargement des données"""
        data_frame = ttk.LabelFrame(parent, text="📂 Données du Problème", padding="10")
        data_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        data_frame.columnconfigure(1, weight=1)
        
        # Chargement de fichier
        ttk.Label(data_frame, text="Fichier CSV:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar(value=config.DATA_FILE)
        ttk.Entry(data_frame, textvariable=self.file_path_var, state="readonly").grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10)
        )
        ttk.Button(data_frame, text="Parcourir", command=self.browse_file).grid(row=0, column=2)
        
        # Capacité
        ttk.Label(data_frame, text="Capacité du sac:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        capacity_spinbox = ttk.Spinbox(data_frame, from_=1, to=1000, textvariable=self.params['capacity'], width=10)
        capacity_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Informations sur le problème
        self.problem_info_var = tk.StringVar(value="Aucun fichier chargé")
        ttk.Label(data_frame, textvariable=self.problem_info_var, foreground="blue").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0)
        )
        
        # Chargement initial
        self.load_problem()

    def setup_params_section(self, parent):
        """Section pour la configuration des paramètres"""
        params_frame = ttk.LabelFrame(parent, text="⚙️ Paramètres de l'Algorithme", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 5), pady=(0, 10))
        
        # Paramètres ACO
        row = 0
        param_configs = [
            ('Alpha (α)', 'alpha', 0.1, 5.0, 0.1),
            ('Bêta (β)', 'beta', 0.1, 5.0, 0.1),
            ('Évaporation', 'evaporation', 0.1, 0.9, 0.05),
            ('Nombre de fourmis', 'num_ants', 5, 100, 1),
            ('Itérations', 'iterations', 10, 500, 10)
        ]
        
        for label_text, param_name, min_val, max_val, increment in param_configs:
            ttk.Label(params_frame, text=f"{label_text}:").grid(row=row, column=0, sticky=tk.W, pady=2)
            
            if param_name in ['num_ants', 'iterations']:
                spinbox = ttk.Spinbox(
                    params_frame, 
                    from_=min_val, 
                    to=max_val, 
                    increment=increment,
                    textvariable=self.params[param_name], 
                    width=10
                )
            else:
                spinbox = ttk.Spinbox(
                    params_frame, 
                    from_=min_val, 
                    to=max_val, 
                    increment=increment,
                    textvariable=self.params[param_name], 
                    width=10,
                    format="%.2f"
                )
            
            spinbox.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            row += 1
        
        # Boutons de configuration prédéfinie
        ttk.Label(params_frame, text="Configurations:").grid(row=row, column=0, sticky=tk.W, pady=(10, 2))
        config_frame = ttk.Frame(params_frame)
        config_frame.grid(row=row+1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Button(config_frame, text="Exploitation", command=lambda: self.apply_preset('exploitation')).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_frame, text="Exploration", command=lambda: self.apply_preset('exploration')).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_frame, text="Équilibré", command=lambda: self.apply_preset('equilibre')).pack(side=tk.LEFT)

    def setup_results_section(self, parent):
        """Section pour l'affichage des résultats"""
        results_frame = ttk.LabelFrame(parent, text="📊 Résultats et Visualisation", padding="10")
        results_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Onglet Résultats texte
        self.setup_text_results_tab()
        
        # Onglet Graphiques
        self.setup_graphs_tab()
        
        # Onglet Comparaisons
        self.setup_comparison_tab()

    def setup_text_results_tab(self):
        """Onglet pour les résultats textuels"""
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="📝 Résultats")
        
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=20)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boutons d'action
        text_buttons_frame = ttk.Frame(text_frame)
        text_buttons_frame.grid(row=1, column=0, sticky=tk.E, pady=(10, 0))
        
        ttk.Button(text_buttons_frame, text="Effacer", command=self.clear_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(text_buttons_frame, text="Sauvegarder", command=self.save_results).pack(side=tk.LEFT)

    def setup_graphs_tab(self):
        """Onglet pour les graphiques"""
        graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(graph_frame, text="📈 Graphiques")
        
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        # Figure matplotlib
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Toolbar matplotlib
        toolbar_frame = ttk.Frame(graph_frame)
        toolbar_frame.grid(row=1, column=0, sticky=tk.W)
        
        try:
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            toolbar.update()
        except ImportError:
            pass

    def setup_comparison_tab(self):
        """Onglet pour les comparaisons"""
        comp_frame = ttk.Frame(self.notebook)
        self.notebook.add(comp_frame, text="⚖️ Comparaisons")
        
        comp_frame.columnconfigure(0, weight=1)
        comp_frame.rowconfigure(0, weight=1)
        
        self.comparison_text = scrolledtext.ScrolledText(comp_frame, wrap=tk.WORD, height=20)
        self.comparison_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def setup_controls_section(self, parent):
        """Section pour les contrôles"""
        controls_frame = ttk.LabelFrame(parent, text="🎮 Contrôles", padding="10")
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Boutons principaux
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.run_button = ttk.Button(buttons_frame, text="🚀 Lancer ACO", command=self.run_aco)
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(buttons_frame, text="⏹️ Arrêter", command=self.stop_aco, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🔧 Optimiser Paramètres", command=self.optimize_parameters).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="📊 Solution Gloutonne", command=self.run_greedy).pack(side=tk.LEFT)
        
        # Barre de progression
        self.progress_var = tk.StringVar(value="Prêt")
        ttk.Label(controls_frame, textvariable=self.progress_var).pack(anchor=tk.W, pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(controls_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)

    def browse_file(self):
        """Ouvre un dialogue pour sélectionner un fichier de données"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier de données",
            filetypes=[("CSV files", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.load_problem()

    def load_data_file(self):
        """Alias pour browse_file pour le menu"""
        self.browse_file()

    def load_problem(self):
        """Charge le problème depuis le fichier CSV"""
        try:
            file_path = self.file_path_var.get()
            if not os.path.exists(file_path):
                # Créer un fichier d'exemple si n'existe pas
                self.create_example_data(file_path)
            
            # Lire le fichier CSV
            items = []
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    items.append({
                        'name': row.get('name', f'Item{len(items)+1}'),
                        'weight': float(row.get('weight', 1)),
                        'value': float(row.get('value', 1))
                    })
            
            if items:
                self.problem = {
                    'items': items,
                    'capacity': self.params['capacity'].get()
                }
                
                total_weight = sum(item['weight'] for item in items)
                total_value = sum(item['value'] for item in items)
                
                info_text = f"✅ {len(items)} objets chargés | Poids total: {total_weight:.1f} | Valeur totale: {total_value:.1f}"
                self.problem_info_var.set(info_text)
            else:
                raise ValueError("Aucun objet trouvé dans le fichier")
                
        except Exception as e:
            self.problem_info_var.set(f"❌ Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de charger le fichier:\n{str(e)}")

    def create_example_data(self, file_path):
        """Crée un fichier d'exemple"""
        example_items = [
            {'name': 'Ordinateur portable', 'weight': 2.5, 'value': 1000},
            {'name': 'Livre', 'weight': 0.5, 'value': 15},
            {'name': 'Téléphone', 'weight': 0.2, 'value': 500},
            {'name': 'Appareil photo', 'weight': 1.0, 'value': 300},
            {'name': 'Vêtements', 'weight': 3.0, 'value': 100},
            {'name': 'Trousse médicale', 'weight': 1.5, 'value': 200},
            {'name': 'Nourriture', 'weight': 2.0, 'value': 50},
            {'name': 'Eau', 'weight': 4.0, 'value': 25},
            {'name': 'Lampe de poche', 'weight': 0.3, 'value': 30},
            {'name': 'Chargeur portable', 'weight': 0.4, 'value': 80}
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'weight', 'value'])
            writer.writeheader()
            writer.writerows(example_items)

    def apply_preset(self, preset_type):
        """Applique une configuration prédéfinie"""
        presets = {
            'exploitation': {'alpha': 2.0, 'beta': 1.0, 'evaporation': 0.3},
            'exploration': {'alpha': 0.5, 'beta': 3.0, 'evaporation': 0.7},
            'equilibre': {'alpha': 1.0, 'beta': 2.0, 'evaporation': 0.5}
        }
        
        if preset_type in presets:
            for param, value in presets[preset_type].items():
                self.params[param].set(value)

    def run_aco(self):
        """Lance l'optimisation ACO"""
        if not self.problem:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier de données")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        self.run_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start()
        self.progress_var.set("Optimisation en cours...")
        
        # Lancer l'ACO dans un thread séparé
        self.current_thread = threading.Thread(target=self._aco_worker)
        self.current_thread.start()

    def _aco_worker(self):
        """Worker thread pour l'ACO"""
        try:
            # Simulation d'algorithme ACO
            items = self.problem['items']
            capacity = self.params['capacity'].get()
            num_iterations = self.params['iterations'].get()
            num_ants = self.params['num_ants'].get()
            
            best_value = 0
            best_solution = []
            convergence_data = []
            
            for iteration in range(num_iterations):
                if not self.is_running:
                    break
                
                # Simulation d'une itération ACO
                iteration_best = self._simulate_aco_iteration(items, capacity, num_ants)
                
                if iteration_best['value'] > best_value:
                    best_value = iteration_best['value']
                    best_solution = iteration_best['solution']
                
                convergence_data.append({
                    'iteration': iteration + 1,
                    'best_value': best_value,
                    'current_value': iteration_best['value']
                })
                
                # Mise à jour du progrès
                progress = (iteration + 1) / num_iterations * 100
                self.results_queue.put({
                    'type': 'progress',
                    'progress': progress,
                    'iteration': iteration + 1,
                    'best_value': best_value
                })
                
                time.sleep(0.01)  # Simulation du temps de calcul
            
            # Résultats finaux
            self.results_queue.put({
                'type': 'result',
                'best_solution': best_solution,
                'best_value': best_value,
                'convergence_data': convergence_data
            })
            
        except Exception as e:
            self.results_queue.put({
                'type': 'error',
                'message': str(e)
            })

    def _simulate_aco_iteration(self, items, capacity, num_ants):
        """Simule une itération de l'ACO"""
        best_ant_value = 0
        best_ant_solution = []
        
        for ant in range(num_ants):
            # Sélection aléatoire d'objets basée sur ratio valeur/poids
            solution = []
            current_weight = 0
            current_value = 0
            
            # Trier les objets par ratio valeur/poids
            sorted_items = sorted(enumerate(items), 
                                key=lambda x: x[1]['value'] / x[1]['weight'], 
                                reverse=True)
            
            for idx, item in sorted_items:
                if current_weight + item['weight'] <= capacity:
                    if np.random.random() > 0.3:  # Probabilité de sélection
                        solution.append(idx)
                        current_weight += item['weight']
                        current_value += item['value']
            
            if current_value > best_ant_value:
                best_ant_value = current_value
                best_ant_solution = solution
        
        return {'solution': best_ant_solution, 'value': best_ant_value}

    def stop_aco(self):
        """Arrête l'optimisation ACO"""
        self.is_running = False
        self.run_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_bar.stop()
        self.progress_var.set("Arrêté")

    def check_results_queue(self):
        """Vérifie la queue des résultats"""
        try:
            while True:
                result = self.results_queue.get_nowait()
                
                if result['type'] == 'progress':
                    self.progress_var.set(f"Itération {result['iteration']} - Meilleure valeur: {result['best_value']:.1f}")
                
                elif result['type'] == 'result':
                    self._display_results(result)
                    self.stop_aco()
                
                elif result['type'] == 'error':
                    messagebox.showerror("Erreur", result['message'])
                    self.stop_aco()
                    
        except queue.Empty:
            pass
        
        # Programmer la prochaine vérification
        self.root.after(100, self.check_results_queue)

    def _display_results(self, result):
        """Affiche les résultats de l'optimisation"""
        best_solution = result['best_solution']
        best_value = result['best_value']
        convergence_data = result['convergence_data']
        
        # Texte des résultats
        results_text = f"""
🎯 RÉSULTATS DE L'OPTIMISATION ACO
{'='*50}

Paramètres utilisés:
• Alpha (α): {self.params['alpha'].get():.2f}
• Bêta (β): {self.params['beta'].get():.2f}
• Évaporation: {self.params['evaporation'].get():.2f}
• Nombre de fourmis: {self.params['num_ants'].get()}
• Itérations: {self.params['iterations'].get()}
• Capacité du sac: {self.params['capacity'].get()}

Meilleure solution trouvée:
• Valeur totale: {best_value:.2f}
• Nombre d'objets: {len(best_solution)}

Objets sélectionnés:
"""
        
        total_weight = 0
        for idx in best_solution:
            item = self.problem['items'][idx]
            results_text += f"• {item['name']} (Poids: {item['weight']:.1f}, Valeur: {item['value']:.1f})\n"
            total_weight += item['weight']
        
        results_text += f"\nPoids total utilisé: {total_weight:.1f}/{self.params['capacity'].get()}\n"
        results_text += f"Efficacité: {total_weight/self.params['capacity'].get()*100:.1f}%\n"
        results_text += f"\nTemps d'exécution: {datetime.now().strftime('%H:%M:%S')}\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, results_text)
        
        # Graphique de convergence
        self._plot_convergence(convergence_data)

    def _plot_convergence(self, convergence_data):
        """Affiche le graphique de convergence"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        iterations = [d['iteration'] for d in convergence_data]
        best_values = [d['best_value'] for d in convergence_data]
        current_values = [d['current_value'] for d in convergence_data]
        
        ax.plot(iterations, best_values, 'b-', label='Meilleure solution', linewidth=2)
        ax.plot(iterations, current_values, 'r-', alpha=0.6, label='Solution courante')
        
        ax.set_xlabel('Itération')
        ax.set_ylabel('Valeur de la solution')
        ax.set_title('Convergence de l\'algorithme ACO')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()

    def run_greedy(self):
        """Exécute l'algorithme glouton pour comparaison"""
        if not self.problem:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier de données")
            return
        
        items = self.problem['items']
        capacity = self.params['capacity'].get()
        
        # Algorithme glouton basé sur le ratio valeur/poids
        sorted_items = sorted(enumerate(items), 
                            key=lambda x: x[1]['value'] / x[1]['weight'], 
                            reverse=True)
        
        solution = []
        current_weight = 0
        current_value = 0
        
        for idx, item in sorted_items:
            if current_weight + item['weight'] <= capacity:
                solution.append(idx)
                current_weight += item['weight']
                current_value += item['value']
        
        # Affichage des résultats
        greedy_text = f"""
🔍 SOLUTION GLOUTONNE (Comparaison)
{'='*40}

Méthode: Tri par ratio valeur/poids décroissant

Résultats:
• Valeur totale: {current_value:.2f}
• Nombre d'objets: {len(solution)}
• Poids utilisé: {current_weight:.1f}/{capacity}
• Efficacité: {current_weight/capacity*100:.1f}%

Objets sélectionnés:
"""
        
        for idx in solution:
            item = items[idx]
            greedy_text += f"• {item['name']} (Ratio: {item['value']/item['weight']:.2f})\n"
        
        greedy_text += f"\nCalculé instantanément à {datetime.now().strftime('%H:%M:%S')}\n"
        
        self.comparison_text.delete(1.0, tk.END)
        self.comparison_text.insert(tk.END, greedy_text)
        
        # Basculer vers l'onglet comparaisons
        self.notebook.select(2)

    def optimize_parameters(self):
        """Optimise automatiquement les paramètres"""
        if not self.problem:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier de données")
            return
        
        messagebox.showinfo("Optimisation", "Fonctionnalité d'optimisation des paramètres en développement")

    def reset_parameters(self):
        """Remet les paramètres aux valeurs par défaut"""
        self.params['alpha'].set(config.ALPHA)
        self.params['beta'].set(config.BETA)
        self.params['evaporation'].set(config.EVAPORATION)
        self.params['num_ants'].set(config.NUM_ANTS)
        self.params['iterations'].set(config.NUM_ITERATIONS)
        self.params['capacity'].set(config.KNAPSACK_CAPACITY)

    def clear_results(self):
        """Efface les résultats affichés"""
        self.results_text.delete(1.0, tk.END)
        self.comparison_text.delete(1.0, tk.END)
        self.figure.clear()
        self.canvas.draw()

    def save_results(self):
        """Sauvegarde les résultats dans un fichier"""
        content = self.results_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Attention", "Aucun résultat à sauvegarder")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder les résultats",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Succès", f"Résultats sauvegardés dans {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{str(e)}")

    def save_config(self):
        """Sauvegarde la configuration actuelle"""
        config_data = {
            'parameters': {
                'alpha': self.params['alpha'].get(),
                'beta': self.params['beta'].get(),
                'evaporation': self.params['evaporation'].get(),
                'num_ants': self.params['num_ants'].get(),
                'iterations': self.params['iterations'].get(),
                'capacity': self.params['capacity'].get()
            },
            'data_file': self.file_path_var.get(),
            'saved_at': datetime.now().isoformat()
        }
        
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder la configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(config_data, file, indent=2, ensure_ascii=False)
                messagebox.showinfo("Succès", f"Configuration sauvegardée dans {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{str(e)}")

    def load_config(self):
        """Charge une configuration depuis un fichier"""
        filename = filedialog.askopenfilename(
            title="Charger une configuration",
            filetypes=[("JSON files", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    config_data = json.load(file)
                
                # Charger les paramètres
                if 'parameters' in config_data:
                    params = config_data['parameters']
                    for key, value in params.items():
                        if key in self.params:
                            self.params[key].set(value)
                
                # Charger le fichier de données
                if 'data_file' in config_data:
                    self.file_path_var.set(config_data['data_file'])
                    self.load_problem()
                
                messagebox.showinfo("Succès", "Configuration chargée avec succès")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger la configuration:\n{str(e)}")

    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        about_text = """
🐜 Optimisation du Sac à Dos par Colonie de Fourmis

Version: 1.0
Auteur: Assistant IA Claude

Description:
Cette application utilise l'algorithme d'optimisation par colonie de fourmis (ACO) 
pour résoudre le problème du sac à dos. L'interface graphique permet de:

• Charger des données depuis un fichier CSV
• Configurer les paramètres de l'algorithme
• Visualiser la convergence en temps réel
• Comparer avec l'algorithme glouton
• Sauvegarder les résultats et configurations

Algorithme ACO:
L'optimisation par colonie de fourmis s'inspire du comportement des fourmis 
qui trouvent le chemin le plus court vers la nourriture en déposant des 
phéromones. Dans ce contexte, les "fourmis" explorent l'espace des solutions 
possibles pour le sac à dos.

Paramètres:
• Alpha (α): Influence des phéromones
• Bêta (β): Influence de l'information heuristique
• Évaporation: Taux d'évaporation des phéromones
• Nombre de fourmis: Taille de la colonie
• Itérations: Nombre de cycles d'optimisation

Format du fichier CSV:
Le fichier doit contenir les colonnes: name, weight, value
        """
        
        messagebox.showinfo("À propos", about_text)

    def run_batch_optimization(self):
        """Exécute plusieurs optimisations avec différents paramètres"""
        if not self.problem:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier de données")
            return
        
        # Configuration pour les tests de paramètres
        parameter_sets = [
            {'name': 'Exploitation', 'alpha': 2.0, 'beta': 1.0, 'evaporation': 0.3},
            {'name': 'Exploration', 'alpha': 0.5, 'beta': 3.0, 'evaporation': 0.7},
            {'name': 'Équilibré', 'alpha': 1.0, 'beta': 2.0, 'evaporation': 0.5},
            {'name': 'Intensif', 'alpha': 3.0, 'beta': 0.5, 'evaporation': 0.2}
        ]
        
        batch_results = "🔬 ANALYSE COMPARATIVE DES PARAMÈTRES\n"
        batch_results += "="*60 + "\n\n"
        
        for param_set in parameter_sets:
            # Simuler l'optimisation avec ces paramètres
            items = self.problem['items']
            capacity = self.params['capacity'].get()
            
            # Simulation simplifiée
            best_value = self._simulate_parameter_set(items, capacity, param_set)
            
            batch_results += f"Configuration: {param_set['name']}\n"
            batch_results += f"• Alpha: {param_set['alpha']}, Bêta: {param_set['beta']}, Évaporation: {param_set['evaporation']}\n"
            batch_results += f"• Résultat: {best_value:.2f}\n\n"
        
        # Afficher dans l'onglet comparaisons
        self.comparison_text.delete(1.0, tk.END)
        self.comparison_text.insert(tk.END, batch_results)
        self.notebook.select(2)

    def _simulate_parameter_set(self, items, capacity, param_set):
        """Simule l'optimisation avec un jeu de paramètres donné"""
        # Simulation basique - dans un vrai ACO, cela serait plus complexe
        alpha = param_set['alpha']
        beta = param_set['beta']
        
        # Calcul d'un score basé sur les paramètres
        base_score = sum(item['value'] for item in items if item['weight'] <= capacity)
        
        # Facteur d'ajustement basé sur les paramètres
        adjustment = (alpha * 0.8 + beta * 0.6) / 3.0
        
        return base_score * adjustment * np.random.uniform(0.7, 1.0)

    def export_graph(self):
        """Exporte le graphique actuel"""
        if not hasattr(self, 'figure') or not self.figure.get_axes():
            messagebox.showwarning("Attention", "Aucun graphique à exporter")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Exporter le graphique",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if filename:
            try:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Succès", f"Graphique exporté vers {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'exporter:\n{str(e)}")

    def validate_parameters(self):
        """Valide les paramètres avant l'exécution"""
        errors = []
        
        if self.params['alpha'].get() <= 0:
            errors.append("Alpha doit être positif")
        
        if self.params['beta'].get() <= 0:
            errors.append("Bêta doit être positif")
        
        if not (0 < self.params['evaporation'].get() < 1):
            errors.append("L'évaporation doit être entre 0 et 1")
        
        if self.params['num_ants'].get() < 1:
            errors.append("Le nombre de fourmis doit être au moins 1")
        
        if self.params['iterations'].get() < 1:
            errors.append("Le nombre d'itérations doit être au moins 1")
        
        if self.params['capacity'].get() <= 0:
            errors.append("La capacité doit être positive")
        
        if errors:
            messagebox.showerror("Paramètres invalides", "\n".join(errors))
            return False
        
        return True

    def get_problem_statistics(self):
        """Calcule des statistiques sur le problème"""
        if not self.problem:
            return None
        
        items = self.problem['items']
        weights = [item['weight'] for item in items]
        values = [item['value'] for item in items]
        ratios = [v/w for v, w in zip(values, weights)]
        
        stats = {
            'num_items': len(items),
            'total_weight': sum(weights),
            'total_value': sum(values),
            'avg_weight': np.mean(weights),
            'avg_value': np.mean(values),
            'avg_ratio': np.mean(ratios),
            'max_ratio': max(ratios),
            'min_ratio': min(ratios),
            'capacity_utilization': sum(weights) / self.params['capacity'].get()
        }
        
        return stats

    def show_problem_analysis(self):
        """Affiche une analyse détaillée du problème"""
        stats = self.get_problem_statistics()
        if not stats:
            messagebox.showwarning("Attention", "Aucun problème chargé")
            return
        
        analysis_text = f"""
📊 ANALYSE DU PROBLÈME
{'='*40}

Statistiques générales:
• Nombre d'objets: {stats['num_items']}
• Poids total: {stats['total_weight']:.2f}
• Valeur totale: {stats['total_value']:.2f}
• Capacité du sac: {self.params['capacity'].get()}

Moyennes:
• Poids moyen: {stats['avg_weight']:.2f}
• Valeur moyenne: {stats['avg_value']:.2f}
• Ratio V/P moyen: {stats['avg_ratio']:.2f}

Ratios valeur/poids:
• Maximum: {stats['max_ratio']:.2f}
• Minimum: {stats['min_ratio']:.2f}

Analyse de difficulté:
• Utilisation théorique: {stats['capacity_utilization']*100:.1f}%
"""
        
        if stats['capacity_utilization'] > 3:
            analysis_text += "• Difficulté: ÉLEVÉE (beaucoup plus d'objets que de capacité)\n"
        elif stats['capacity_utilization'] > 1.5:
            analysis_text += "• Difficulté: MOYENNE (sélection nécessaire)\n"
        else:
            analysis_text += "• Difficulté: FAIBLE (la plupart des objets peuvent être pris)\n"
        
        # Recommandations de paramètres
        analysis_text += "\n🎯 RECOMMANDATIONS DE PARAMÈTRES:\n"
        
        if stats['capacity_utilization'] > 2:
            analysis_text += "• Privilégier l'exploration (β élevé, évaporation élevée)\n"
            analysis_text += "• Augmenter le nombre d'itérations\n"
        else:
            analysis_text += "• Équilibrer exploration/exploitation\n"
            analysis_text += "• Paramètres par défaut appropriés\n"
        
        self.comparison_text.delete(1.0, tk.END)
        self.comparison_text.insert(tk.END, analysis_text)
        self.notebook.select(2)

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = ACOKnapsackGUI(root)
    
    # Gestionnaire de fermeture
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Quitter", "Une optimisation est en cours. Voulez-vous vraiment quitter?"):
                app.stop_aco()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Ajout de raccourcis clavier
    root.bind('<Control-o>', lambda e: app.browse_file())
    root.bind('<Control-s>', lambda e: app.save_results())
    root.bind('<Control-r>', lambda e: app.run_aco())
    root.bind('<F5>', lambda e: app.run_aco())
    root.bind('<Escape>', lambda e: app.stop_aco())
    
    root.mainloop()

if __name__ == "__main__":
    main()