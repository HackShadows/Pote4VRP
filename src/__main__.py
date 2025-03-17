from classes import Flotte, Trajet, Client
from affichage import affichage_console, affichage_graphique
import filesIO as fio

from serveur import lancer_serveur

from pathlib import Path
import os
from datetime import datetime

from typing import Any, IO, Optional





AFFICHAGE = 0b_01
CONSOLE   = 0b_00
GRAPHIQUE = 0b_01

DETAILS   = 0b_10




def générer_solution_aléatoire(métadonnées :dict[str, Any], dépôt :Client, clients :list[Client]) -> Flotte :
	flotte = Flotte(métadonnées["MAX_QUANTITY"])
	trajet = Trajet(dépôt)
	for i, cli in enumerate(clients) :

		if trajet.marchandise > flotte.capacite / 2 :
			flotte.ajouter_trajet(trajet)
			trajet = Trajet(dépôt)

		trajet.ajouter_client(i, cli)
	flotte.ajouter_trajet(trajet)
	return flotte



def approximation_solution(fichier :str|Path|IO[str], mode :int = 1, sortie :Optional[str|Path|IO[str]] = None) :
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
	sortie : path_like | stream_like
		Chemin du fichier vrp où écrire les informations de la solution.
		Si non-spécifié, le chemin est choisi automatiquement (data/out/result_{datetime.now()}.vrp)
	
	Erreurs
	-------
	ValueError
		Le fichier d'entré contient plus d'un dépôt.
	Toutes les erreurs de filesIO.importer_vrp
	"""
	nom_fichier = None

	if isinstance(fichier, (str, Path)) :
		nom_fichier = fichier_in = Path(fichier)
	else :
		fichier_in = fichier
		try :
			if isinstance(fichier.name, str) :
				nom_fichier = Path(fichier_name)
		except AttributeError : pass

	if isinstance(sortie, (str, Path)) :
		nom_fichier = fichier_out = Path(sortie)
	elif sortie is not None :
		fichier_out = sortie
		try :
			if isinstance(sortie.name, str) :
				nom_fichier = Path(sortie.name)
		except AttributeError : pass

	if nom_fichier is None :
		nom_fichier = Path(f"data/out/result_{datetime.now()}.vrp")
		if sortie is None :
			sortie = nom_fichier



	métadonnées, dépôts, clients = fio.importer_vrp(fichier_in)
	if len(dépôts) != 1 :
		raise ValueError("L'algorithme ne peut gérer qu'un seul dépôt à la fois.")
	dépôt = dépôts[0]



	flotte = générer_solution_aléatoire(métadonnées, dépôt, clients)
	positions = [cli.pos for cli in clients]

	détails = bool(mode & DETAILS)
	if   (mode & AFFICHAGE) == CONSOLE   : affichage_console (nom_fichier.stem, positions, flotte, détails)
	elif (mode & AFFICHAGE) == GRAPHIQUE : affichage_graphique (positions, flotte, détails)
	


	fio.exporter_vrp(fichier_out, flotte, **métadonnées)





def fonction_traitement(nom_fichier, fichier_données) :
	chemin = Path("data")
	nom_fichier = Path(nom_fichier)

	approximation_solution(fichier_données, CONSOLE, chemin/"out"/nom_fichier)

	return (
		chemin/"out"/nom_fichier,
		f"""<h2>{nom_fichier}</h2><img src="{chemin/'out'/(nom_fichier.stem + '.svg')}">"""
	)





def main_dev() :
	"""La fonction main qui sera utilisé par les dévelepeurs"""
	fichiers = [101, 102, 111, 112, 201, 202, 1101, 1102, 1201, 1202]

	# affichage = int(input("Affichage console (1), Affichage graphique (2), Affichage console détaillé (3), Affichage graphique détaillé (4) :\n"))
	# for num in fichiers : approximation_solution(f"data/data{num}.vrp", affichage)

	num = fichiers[0]
	approximation_solution(f"data/in/data{num}.vrp", CONSOLE)



def main() :
	"""La fonction main qui sera utilisé par les utilisateurs"""
	lancer_serveur(fonction_traitement)



if __name__ == '__main__' :
	if False : main_dev()
	else : main()
