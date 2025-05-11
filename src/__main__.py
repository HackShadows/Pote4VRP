from classes import Flotte, Trajet, Client
from affichage import affichage_console, affichage_graphique, sauvegarde_image_flotte
import filesIO as fio

from serveur import lancer_serveur
from io import StringIO

from pathlib import Path
import os
from datetime import datetime

from typing import Any, IO, Optional





AFFICHAGE = 0b_001
CONSOLE   = 0b_000
GRAPHIQUE = 0b_001

DETAILS = 0b_010
VISUEL  = 0b_100




def générer_solution_aléatoire(métadonnées :dict[str, Any], dépôt :Client, clients :list[Client], capacite :bool=False, remplissage :float=0.5, temps :bool=False) -> Flotte :
	"""
	Génère une solution initiale.

	Paramètres
	----------
	métadonnées : dict[str, Any]
		Dictionnaire contenant les métadonnées présentes dans le fichier initial.
	dépôt : Client
		Client contenant toutes les informations du dépôt.
	clients : list[Client]
		Liste des clients à mettre dans la solution initiale.
	capacite : bool
		True pour prendre en compte la contrainte de capacité, False sinon.
	remplissage : float
		Pourcentage de remplissage des camions (compris entre 0.01 et 1.00)
	temps : bool
		True pour prendre en compte la contrainte de temps, False sinon.
	
	Renvoie
	-------
	Une flotte initiale.
	"""
	assert isinstance(remplissage, float) and 0 < remplissage < 1 and isinstance(capacite, bool) and isinstance(temps, bool) and isinstance(dépôt, Client) and isinstance(clients, list)
	
	flotte = Flotte(métadonnées["MAX_QUANTITY"])
	trajets = [Trajet(dépôt, capacite, temps)]
	for cli in clients :
		assert isinstance(cli, Client)
		continuer = True
		a_ajouter = []
		for j in range(len(trajets)):
			if not continuer: break
			if trajets[j].nb_clients > 0:
				if capacite and trajets[j].marchandise > flotte.capacite * remplissage or temps and trajets[j].horaires[-1] + cli.temps_livraison >= dépôt.intervalle_livraison[1]:
					a_ajouter.append(j)
					continue
			for i in range(trajets[j].nb_clients+1):
				if temps and trajets[j].maj_horaires(i, cli, False):
					trajets[j].ajouter_client(i, cli)
					continuer = False
					break
		for i in a_ajouter[::-1]: flotte.ajouter_trajet(trajets.pop(i))
		
		if continuer:
			trajets.append(Trajet(dépôt, capacite, temps))
			trajets[-1].ajouter_client(0, cli)

	
	for trajet in trajets: flotte.ajouter_trajet(trajet)
	
	return flotte



def approximation_solution(fichier :str|Path|IO[str], mode :int = CONSOLE, capacite :bool=False, remplissage :float=0.5, temps :bool=False, sortie :Optional[str|Path|IO[str]] = None) :
	"""
	Calcule et affiche un itinéraire de livraison proche de l'optimal.
	
	Paramètres
	----------
	fichier : path_like | stream_like
		Chemin du fichier vrp contenant les informations sur les clients à livrer.
		Ex : data/in/data101.vrp
	mode : int
		Entier permettant de spécifier l'affichage désiré.
		Affichage console (0), Affichage graphique (1), 
		Affichage console détaillé (2), Affichage graphique détaillé (3)
	capacite : bool
		True pour prendre en compte la contrainte de capacité, False sinon.
	remplissage : float
		Pourcentage de remplissage des camions (compris entre 0.01 et 1.00)
	temps : bool
		True pour prendre en compte la contrainte de temps, False sinon.
	sortie : path_like | stream_like
		Chemin du fichier vrp où écrire les informations de la solution.
		Si non-spécifié, le chemin est choisi automatiquement (data/out/result_{datetime.now()}.vrp)
	
	Erreurs
	-------
	ValueError
		Le fichier d'entrée contient plus d'un dépôt.
	Toutes les erreurs de filesIO.importer_vrp
	"""
	assert isinstance(capacite, bool) and isinstance(temps, bool) and isinstance(remplissage, float)
	chemin_fichier = None

	if isinstance(fichier, (str, Path)) :
		chemin_fichier = fichier_in = Path(fichier)
	else :
		fichier_in = fichier
		try :
			if isinstance(fichier.name, str) :
				chemin_fichier = Path(fichier.name)
		except AttributeError : pass

	if isinstance(sortie, (str, Path)) :
		chemin_fichier = fichier_out = Path(sortie)
	elif sortie is not None :
		fichier_out = sortie
		try :
			if isinstance(sortie.name, str) :
				chemin_fichier = Path(sortie.name)
		except AttributeError : pass

	if chemin_fichier is None :
		date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
		chemin_fichier = Path(f"data/out/result_{date}.vrp")
	if sortie is None :
		fichier_out = chemin_fichier.parent.parent/"out"/chemin_fichier.name



	métadonnées, dépôts, clients = fio.importer_vrp(fichier_in)
	if len(dépôts) != 1 :
		raise ValueError("L'algorithme ne peut gérer qu'un seul dépôt à la fois.")
	dépôt = dépôts[0]



	flotte = générer_solution_aléatoire(métadonnées, dépôt, clients, capacite, remplissage, temps)
	positions = [cli.pos for cli in clients]

	détails = bool(mode & DETAILS)
	if   (mode & AFFICHAGE) == CONSOLE   : affichage_console (flotte, détails)
	elif (mode & AFFICHAGE) == GRAPHIQUE : affichage_graphique (positions, flotte, détails)

	if mode & VISUEL : sauvegarde_image_flotte(chemin_fichier.stem, positions, flotte)
	


	fio.exporter_vrp(fichier_out, flotte, **métadonnées)





def fonction_traitement(nom_fichier :str, fichier_données :bytes) -> Optional[str] :
	try :
		fichier_données = StringIO(fichier_données.decode())
		approximation_solution(fichier_données, CONSOLE|VISUEL, True, 0.5, True, "data/out/" + nom_fichier + ".vrp")
	except Exception as e :
		return repr(e)
	else : return None





def main_dev() :
	"""La fonction main qui sera utilisé par les dévelepeurs"""
	fichiers = [101, 102, 111, 112, 201, 202, 1101, 1102, 1201, 1202]

	# affichage = int(input("Affichage console (1), Affichage graphique (2), Affichage console détaillé (3), Affichage graphique détaillé (4) :\n"))
	# for num in fichiers : approximation_solution(f"data/data{num}.vrp", affichage)

	num = fichiers[0]
	
	contrainte_capacite = True
	remplissage_initial = 0.5
	contrainte_temps = True
	
	approximation_solution(f"data/in/data{num}.vrp", CONSOLE, contrainte_capacite, remplissage_initial, contrainte_temps)



def main() :
	"""La fonction main qui sera utilisé par les utilisateurs"""
	lancer_serveur(fonction_traitement)



if __name__ == '__main__' :
	if True : main_dev()
	else : main()
