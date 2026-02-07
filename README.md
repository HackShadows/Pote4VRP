# POTE4 VRP - Optimiseur de Tournées de Livraison

![Language](https://img.shields.io/badge/Language-Python_3\.11-3776ab)
![Library](https://img.shields.io/badge/Library-Matplotlib-orange)
![Framework](https://img.shields.io/badge/Template-Jinja2-b41717)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

![Aperçu de l'optimisation](images/solution_2.svg)

**POTE4-vrp** est une application complète permettant d'optimiser des trajets de livraison (*Vehicle Routing Problem*).

L’application se compose d'un serveur Python local qui exécute des algorithmes méta-heuristiques (Relocate, Exchange, 2-Opt, Cross-Exchange) sur des fichiers de données `.vrp`, et d'une interface web de visualisation.
Projet réalisé dans le cadre du cursus PEIP2 (S4, Polytech Lyon).

## Fonctionnalités

* Optimisation de tournées de livraison via algorithmes heuristiques.
* Visualisation graphique des trajets en temps réel.
* Analyse statistique des solutions.

## Architecture Technique

* **Langage :** Python 3.11
* **Web :** Serveur HTTP natif + Jinja2
* **Calcul :** NumPy, Matplotlib

### Documentation

Vous pouvez retrouver tous les documents relatifs à la conception et au suivi du projet dans le dossier `project-files/` :

* **[Cahier des charges](project-files/CahierDesCharges.pdf)** : Définition des besoins et contraintes.
* **[Diagramme de Gantt](project-files/DiagrammeGantt.pdf)** : Planification du développement.
* **[Présentation du projet](project-files/Peip2_projet_INFO4.pdf)** : Présentation des contraintes/consignes.
* **[Rapport final](project-files/Rapport-POTE4-VRP.pdf)** : Analyse détaillée des algorithmes et résultats.
* **[Soutenance](project-files/Présentation_POTE4.pdf)** : Support de présentation final.

## Structure du Projet

```text
pote4-vrp/
├── README.md
├── LICENSE
├── requirements.txt
├── data/                     # Scripts d'analyse et fichiers .vrp
├── interface_utilisateur/    # Front-end (Templates & Static)
├── project-files/            # Rapports PDF
└── src/                      # Code source Back-end
    ├── affichage.py
    ├── classes.py
    ├── opérateurs.py
    ├── serveur.py
    └── ...
```

## Installation

1. **Environnement virtuel :**

```bash
python3 -m venv .vepote
source .vepote/bin/activate  # Linux/Mac
.vepote\Scripts\Activate   # Windows
```

2. **Dépendances :**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Lancement :**
```bash
python3 src
```
L'application est accessible sur `http://localhost:8080`.

4. **Tests :**
```bash
python3 -m unittest discover src
```

## Auteurs

* **Marius CISERANE**
* **Matthias BOULLOT**

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.