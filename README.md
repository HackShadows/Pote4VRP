POTE4 VRP
=========

POTE4-vrp est une application permettant d'optimiser des trajets de livraison.
L’application consiste d’un serveur python tournant en local et s’occupant de faire tourner des algorithmes sur les fichiers de données envoyés. L’interface client se fait à travers une page web dans un navigateur qui communique avec le serveur.

Le cahier des charges associé : 



Installation
------------

Pour installer, téléchargez ce dépôt ou vous le souhaitez sur votre ordinateur, là où vous le souhaitez, puis tapez la commande suivante dans un terminal :
```sh
cd chemin/vers/pote4-vrp
```
Il est nécessaire de créer un environnement virtuel Python pour lancer
l'application. Cela peut se faire via la commande suivante (pour créer
l'environnement dans le répertoire `.venv`) :
```sh
python3 -m venv .vepote
```
Pour activer cet environnement dans votre shell :
```sh
source .vepote/bin/activate  # sous linux, macos
.vepote\Scripts\activate  # sous windows
```
Il faut ensuite installer les dépendances du projet
```sh
# python3.11 -m ensurepip  # si pip non disponible avec python
pip install --upgrade pip  # au moins la version 20.3 de pip
pip install -r requirements.in
```



Utilisation
-----------

Pour lancer l’application, assurez vous que le terminal soit ouvert au niveau du répertoire de l’application (pote4-vrp), et assurez vous que  l’environnement est activé.
Il suffit de taper la commande
```sh
python3 src
```
L’application devrait automatiquement s'ouvrir dans votre navigateur par défaut.

Quand vous quittez l’application, **pensez à bien à l’arrêter** en tapant `^C` dans le terminal où elle s’exécute.

Tests
-----
Pour lancer les tests, assurez vous que le terminal soit ouvert au niveau du répertoire de l’application (pote4-vrp), et assurez vous que l’environnement est activé.
Il suffit de taper la commande :
```sh
python3 -m unittest src/test # en théorie
```



Documentation
-------------

### L’arborescence du projet
```
pote4-vrp/
├── CC_DiagrammeGantt.pdf   Le cahier des charges et diagramme de Gantt du projet
├── README.md               Le fichier que vous lisez
├── data/                   Le dossier où sont stockés les fichiers de données de manière intermédiaire
│ ├── in/                      Les fichiers entrants
│ └── out/                     Les fichiers sortants
├── interface_utilisateur/  Le site web (HTML, CSS, JS)
│ ├── static/                  Les fichiers statics
│ │ ├── css/                      Le CSS
│ │ └── javascript/               Le JS
│ └── templates/               Les templates HTML
└── src/                    Le code source de l'application
  ├── __main__.py           Le fichier principal qui lance l'application
  ├── ...
  └── test/                 Le répertoire des tests
```
