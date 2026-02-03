# POTE4 VRP - Optimiseur de Tournées de Livraison

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Matplotlib](https://img.shields.io/badge/Library-Matplotlib-orange.svg)
![Jinja2](https://img.shields.io/badge/Template-Jinja2-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Terminé-success.svg)

![Aperçu de l'optimisation](images/solution_2.svg)

**POTE4-vrp** est une application complète permettant d'optimiser des trajets de livraison (*Vehicle Routing Problem*).

L’application se compose d'un **serveur Python** local qui exécute des algorithmes méta-heuristiques (Relocate, Exchange, 2-Opt, Cross-Exchange) sur des fichiers de données `.vrp`. L’interface utilisateur est une **application web** moderne permettant de visualiser les trajets et les gains d'optimisation en temps réel.

---

## 🛠️ Installation

### 1. Cloner le projet
Téléchargez ce dépôt sur votre ordinateur et placez-vous dans le dossier :
```sh
cd chemin/vers/pote4-vrp
```

### 2. Créer l'environnement virtuel

Il est nécessaire de créer un environnement virtuel Python pour isoler les dépendances :

```sh
python3 -m venv .vepote
```

### 3. Activer l'environnement
* **Sous Linux / Mac :**
```sh
source .vepote/bin/activate
```
* **Sous Windows (PowerShell) :**
```sh
.vepote\Scripts\Activate
```

### 4. Installer les dépendances
```sh
pip install --upgrade pip
pip install -r requirements.txt
```

## 🚀 Utilisation

1.  Assurez-vous que votre terminal est ouvert à la racine du projet et que l'environnement virtuel est activé (`(.vepote)` doit apparaître).
2.  Lancez le serveur :

```bash
python3 src
```
L’application devrait s'ouvrir automatiquement dans votre navigateur par défaut (sinon, rendez-vous sur l'URL indiquée dans le terminal, généralement `http://localhost:8080`).

Pour arrêter le serveur, tapez **Ctrl+C** dans le terminal.

## 🧪 Tests

Des tests unitaires sont disponibles pour vérifier le bon fonctionnement des classes et des opérateurs. Pour les lancer :

```bash
python3 -m unittest discover src
```

## 📂 Documentation & Architecture

### Arborescence du projet

```text
pote4-vrp/
├── README.md                 # Documentation principale
├── LICENSE                   # Licence MIT du projet
├── requirements.txt          # Liste des dépendances
├── data/                     # Gestion des données
│   ├── analyse.py            # Scripts d'analyse statistique
│   ├── in/                   # Dossier d'entrée pour les fichiers .vrp
│   └── out/                  # Dossier de sortie (résultats générés)
├── images/                   # Images pour le README et les rapports
├── interface_utilisateur/    # Front-end de l'application
│   ├── static/               # Assets (CSS, JS, Images)
│   └── templates/            # Templates HTML (Jinja2)
├── project-files/            # Rapports et présentations PDF
└── src/                      # Code source Python (Back-end)
    ├── affichage.py          # Génération des graphiques (Matplotlib)
    ├── classes.py            # Définition des structures (Client, Trajet, Flotte)
    ├── opérateurs.py         # Algorithmes d'optimisation (Heuristiques)
    ├── serveur.py            # Gestion du serveur HTTP
    └── ...
```

### Documents du projet

Vous pouvez retrouver tous les documents relatifs à la conception et au suivi du projet dans le dossier `project-files/` :

* 📄 **[Cahier des charges](project-files/CahierDesCharges.pdf)** : Définition des besoins et contraintes.
* 📅 **[Diagramme de Gantt](project-files/DiagrammeGantt.pdf)** : Planification du développement.
* 📊 **[Présentation du projet](project-files/Peip2_projet_INFO4.pdf)** : Support de présentation initial.
* 📝 **[Rapport final](project-files/Rapport-POTE4-VRP.pdf)** : Analyse détaillée des algorithmes et résultats.
* 🎓 **[Soutenance](project-files/Présentation_POTE4.pdf)** : Support de présentation final.

---

## 👥 Auteurs

Projet réalisé dans le cadre du cursus PEIP2 à Polytech Lyon.

* **Marius CISERANE**
* **Matthias BOULLOT**