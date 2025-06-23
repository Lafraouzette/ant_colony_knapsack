Voici un fichier *`README.md` complet et professionnel* pour ton mini-projet *"Optimisation du sac à dos par l’algorithme des colonies de fourmis (ACO)"* :

---

```markdown
# 🐜 Optimisation du problème du sac à dos par l’algorithme des colonies de fourmis (ACO)

## 📌 Description

Ce projet implémente une solution d’intelligence artificielle pour le problème du sac à dos 0-1, en utilisant l’algorithme bio-inspiré des colonies de fourmis (Ant Colony Optimization - ACO)*.

Le but est de sélectionner un sous-ensemble d’objets ayant une *valeur maximale* tout en respectant la *capacité maximale du sac*. L’algorithme simule plusieurs fourmis virtuelles qui coopèrent indirectement via un système de *phéromones* pour converger vers une solution optimale.

---
## 📁 Structure du projet


---

## ⚙️ Configuration (fichier `config.py`)

```python
ALPHA = 1               # Importance des phéromones
BETA = 2                # Importance de l’heuristique (valeur/poids)
EVAPORATION = 0.5       # Taux d’évaporation des phéromones
NUM_ANTS = 30           # Nombre de fourmis
NUM_ITERATIONS = 100    # Nombre d’itérations
KNAPSACK_CAPACITY = 50  # Capacité maximale du sac
````

---

## 🧠 Algorithme ACO – Étapes

1. Initialisation des objets, des phéromones et des paramètres.
2. À chaque itération :

   * Chaque fourmi construit une solution (choix d’objets).
   * On évalue la solution (valeur et poids).
   * Mise à jour des phéromones.
3. On conserve la meilleure solution trouvée.




---

## 🚀 Exécution

```bash
python main.py
```

Le script affichera la **meilleure combinaison d’objets** sélectionnée par l’algorithme avec :

* leur poids total
* leur valeur totale

---

## 📈 Résultats attendus

* Optimisation de la valeur totale du sac
* Solutions évolutives avec chaque itération
* (Optionnel) Visualisation graphique de la convergence

---


## 👨‍💻 Auteur

> Projet réalisé par Mouhssine LAFRAOUZI – Étudiant en Intelligence Artificielle
> Date : Juin 2025

