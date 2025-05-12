from ..classes import Client


from typing import Any, IO, Optional
from pathlib import Path
from random import randrange







def formate_métadonnée(nom :str, valeur :Any) -> str :
	"""
	Formate une métadonnée en string.

	Paramètres
	----------
	nom : string
		Nom de la métadonnée
	valeur : any
		Valeur de la métadonnée
	
	Renvoie
	-------
	La ligne correspondant à la métadonnée.
	"""
	return f"{nom} : {valeur!s}\n"

def formate_entête(nom :str, attributs :list[str]) -> str :
	"""
	Formate un entête en string.

	Paramètres
	----------
	nom : string
		Nom de l'entête
	attributs : list of strings
		Attributs de l'entête
	
	Renvoie
	-------
	La ligne correspondant à l'entête.
	"""
	return f"{nom} [{' '.join(attributs)}] :\n"





def générer_vrp(fichier              :str|Path|IO[str]
              , nb_dépôts            :int
              , nb_clients           :int
              , capacité             :int
              , taille_environnement :Optional[tuple[int, int]] = None
	      , temps_fin            :Optional[int]             = None
              , **métadonnées        :Any) :
	"""
	Génère une table de clients dans un fichier .vrp. Example : générer_vrp("data/in/test.vrp", 1, 500, 500)

	Paramètres
	----------
	fichier : path_like
		Le nom du fichier où écrire les données.
	fichier : stream_like
		Un flux ouvert sur l'emplacement où écrire les données.
	flotte : Flotte
		La flotte à exporter.
	**métadonnées : dict of strings to values
		Les valeurs de certaines métadonnées (comme NAME ou COMMENT, etc). Toutes les métadonnées ont une valeur par défaut.


	Erreurs
	-------
	ValueError
		La valeur d'une métadata n'est pas correcte.
	"""
	if isinstance(fichier, (str, Path)) :
		métadonnées.setdefault("NAME", fichier)
		with open(fichier, 'w') as f :
			return générer_vrp(f, nb_dépôts, nb_clients, capacité, taille_environnement, temps_fin, **métadonnées)
	

	assert nb_dépôts > 0 and nb_clients > 0 and capacité > 0, taille_environnement[0] > 0 and taille_environnement[1] > 0 and temps_fin > 0

	if taille_environnement is None : taille_environnement = (200, 100)
	if temps_fin            is None : temps_fin            = 200



	dépôts = [Client(
		f"d{i}",
		tuple(randrange(taille_environnement[i]) for i in range(2)),
		(0, temps_fin)
	) for i in range(nb_dépôts)]

	clients = [Client(
		f"c{i}",
		tuple(randrange(taille_environnement[i]) for i in range(2)),
		tuple(sorted(randrange(1, temps_fin) for _ in range(2))),
		randrange(1, capacité // 2 + 1),
		randrange(1, 20)
	) for i in range(nb_clients)]


	if (v := métadonnées.setdefault("NAME"        , ""         )) != ""         : pass
	if (v := métadonnées.setdefault("COMMENT"     , ""         )) != ""         : pass
	if (v := métadonnées.setdefault("TYPE"        , "vrptw"    )) != "vrptw"    : raise ValueError(f"Type de données non supporté : \"{v}\" (attendu vrptw)")
	if (v := métadonnées.setdefault("COORDINATES" , "cartesian")) != "cartesian": raise ValueError(f"Type de coordonées non supporté : \"{v}\" (attendu cartesian)")
	if (v := métadonnées.setdefault("NB_DEPOTS"   , nb_dépôts  )) != nb_dépôts  : raise ValueError(f"Incohérence dans le nombre de dépôts : résultat={nb_dépôts} métadonnées={v}")
	if (v := métadonnées.setdefault("NB_CLIENTS"  , nb_clients )) != nb_clients : raise ValueError(f"Incohérence dans le nombre de clients : résultat={nb_clients} métadonnées={v}")
	if (v := métadonnées.setdefault("MAX_QUANTITY", capacité   )) != capacité   : raise ValueError(f"Incohérence dans la capacité maximale des véhicules : résultat={capacité} métadonnées={v}")



	for nom, valeur in métadonnées.items() :
		fichier.write(formate_métadonnée(nom, valeur))
	fichier.write("\n")



	fichier.write(formate_entête("DATA_DEPOTS", ["idName", "x", "y", "readyTime", "dueTime"]))
	for dépôt in dépôts :
		ID = dépôt.id; X, Y = dépôt.pos; DÉBUT_H, FIN_H = dépôt.intervalle_livraison
		fichier.write(f"{ID}\t{X}\t{Y}\t{DÉBUT_H}\t{FIN_H}\n")
	fichier.write("\n")


	fichier.write(formate_entête("DATA_CLIENTS", ["idName", "x", "y", "readyTime", "dueTime", "demand", "service"]))
	for client in clients :
		ID = client.id; X, Y = client.pos; DÉBUT_H, FIN_H = client.intervalle_livraison; QUANT = client.demande; DURÉE = client.temps_livraison
		fichier.write(f"{ID}\t{X}\t{Y}\t{DÉBUT_H}\t{FIN_H}\t{QUANT}\t{DURÉE}\n")
	fichier.write("\n")
