from classes import Flotte, Trajet
from affichage import affichage_console, affichage_graphique
import filesIO as fio

from pathlib import Path





AFFICHAGE = 0b_01
CONSOLE   = 0b_00
GRAPHIQUE = 0b_01

DETAILS   = 0b_10



def approximation_solution(fichier :str, mode :int = 1) :
	"""
	Calcule et affiche un itinéraire de livraison proche de l'optimal.
	
	Paramètres
	----------
	fichier : str
		Chemin du fichier vrp contenant les informations sur les clients à livrer.
		Ex : data/data101.vrp
	mode : int
		Entier permettant de spécifier l'affichage désiré.
		Affichage console (0), Affichage graphique (1), 
		Affichage console détaillé (2), Affichage graphique détaillé (3)
	
	Erreurs
	-------
	ValueError
		Le fichier d'entré contient plus d'un dépôt.
	Toutes les erreurs de filesIO.importer_vrp
	"""
	fichier_in  = Path(fichier)
	fichier_out = Path(fichier_in.parent, f"out_{fichier_in.name}")


	métadonnées, dépôts, clients = fio.importer_vrp(fichier_in)
	if len(dépôts) != 1 :
		raise ValueError("L'algorithmes ne peut gérer qu'un seul dépôt à la fois.")
	dépôt = dépôts[0]


	positions = [cli.pos for cli in clients]


	flotte = Flotte(métadonnées["MAX_QUANTITY"])
	trajet = Trajet(dépôt)
	for i, cli in enumerate(clients) :

		if trajet.marchandise > flotte.capacite / 2 :
			flotte.ajouter_trajet(trajet)
			trajet = Trajet(dépôt)

		trajet.ajouter_client(i, cli)
	flotte.ajouter_trajet(trajet)


	détails = bool(mode & DETAILS)
	if   (mode & AFFICHAGE) == CONSOLE   : affichage_console(flotte,                détails)
	elif (mode & AFFICHAGE) == GRAPHIQUE : affichage_graphique(positions, flotte,   détails)


	fio.exporter_vrp(fichier_out, flotte, **métadonnées)





def main_dev() :
	"""La fonction main qui sera utilisé par les dévelepeurs"""
	fichiers = [101, 102, 111, 112, 201, 202, 1101, 1102, 1201, 1202]

	# affichage = int(input("Affichage console (1), Affichage graphique (2), Affichage console détaillé (3), Affichage graphique détaillé (4) :\n"))
	# for num in fichiers : approximation_solution(f"data/data{num}.vrp", affichage)

	num = fichiers[0]
	approximation_solution(f"data/data{num}.vrp", CONSOLE)



def main() :
	"""La fonction main qui sera utilisé par les utilisateurs"""
	pass



if __name__ == '__main__' :
	if True : main_dev()
	else : main()
