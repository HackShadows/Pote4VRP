"""
Met à disposition des fonctions permettant l'importation et l'exportation
des jeux de données dans le programme.
"""

from classes import Client, Flotte

import re, warnings
from pathlib import Path

from typing import Any, IO





class ParsingError(Exception) :
	pass





MÉTADONNÉE_CONNUES = {
	"NAME"         : str,
	"COMMENT"      : str,
	"TYPE"         : str,
	"COORDINATES"  : str,
	"NB_DEPOTS"    : int,
	"NB_CLIENTS"   : int,
	"MAX_QUANTITY" : int,
}





_PATTERN_MÉTADONNÉES = re.compile(r"^([A-Z_]+)\s*:\s*(.*)\n$")

def extrait_métadonnée(ligne :str) -> tuple[str, str] :
	"""
	Extrait le nom et la valeur d'une métadonnée.

	Paramètres
	----------
	ligne : string
		La ligne d'où extraire la métadonnée, elle doit se terminer par un symbol \\n.
	
	Renvoie
	-------
	Le nom de la métadonnée et sa valeur non-interprétée.

	Erreurs
	-------
	ParsingError
		La métadonnée est mal formée.
	"""
	match = _PATTERN_MÉTADONNÉES.match(ligne)
	if match is None or len(match.groups()) != 2 :
		raise ParsingError(f"La métadonné \"{ligne}\" ne suit pas le format \"<NOM_DE_LA_METADONNE> : <valeur>\".")
	return match.groups()

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



_PATTERN_ENTÊTE = re.compile(r"^([A-Z_]+)\s*\[(\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)+)\]\s*:\n$")

def extrait_entête(ligne :str) -> tuple[str, list[str]] :
	"""
	Extrait le nom et les attributs d'un entête.

	Paramètres
	----------
	ligne : string
		La ligne d'où extraire l'entête, elle doit se terminer par un symbol \\n.

	Renvoie
	-------
	Le nom de l'entête et le nom de ses attributs.

	Erreurs
	-------
	ParsingError
		L'entête est mal formée.
	"""
	match = _PATTERN_ENTÊTE.match(ligne)
	if match is None or len(match.groups()) != 2 :
		raise ParsingError(f"L'entête de tableau \"{ligne}\" ne suit pas le format \"<NOM_DU_TABLEAU> [ <nom_de_la_colonne> <...> ] :\"")
	nom, attributs = match.groups()
	return nom, attributs.strip().split()

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





def _cherche_entête(nom_tableau :str, entête :list[str], données :list[str]) -> list[int] :
	"""
	Recherche les données dans 'entête' et lève une exception si elles n'existent pas.

	Paramètres
	----------
	nom_tablea : string
		Le nom du tableau auquel appartient l'entête. Demander pour donner plus d'information en cas d'erreur.
	entête : list of strings
		L'entête du tableau, l'ordre des attributs doit être conservé.
	données : list of strings
		Les données recherchées dans l'entête.
	
	Renvoie
	-------
	Une liste contenant pour chaque donnée, son index dans l'entête.

	Erreurs
	-------
	ParsingError
		La donnée n'a pas été trouvé dans l'entête.
	"""
	entête = {name.lower() : i for i, name in enumerate(entête)}

	résultat = list()
	for donnée in données :
		index = entête.get(donnée.lower())
		if index is None :
			raise ParsingError(f"Le tableau {nom_tableau} ne contient pas l'attribut '{donnée}'")
		résultat.append(index)
	
	return résultat



def importer_vrp(fichier :str|Path|IO[str]) -> tuple[dict[str, Any], list[Client], list[Client]] :
	"""
	Importe les données du fichier .vrp dans le programme.
	La fonction parse les métadonnées, puis se met à la recherche des tableaux 'DATA_DEPOTS' et 'DATA_CLIENTS'.

	Paramètres
	----------
	fichier : path_like
		Le nom du fichier à importer.
	fichier : stream_like
		Un flux ouvert sur le fichier à importer.
	
	Renvoie
	-------
	Un tuple contenant respectivement la liste des dépots et la liste des clients.

	Avertissements
	--------------
	UserWarning
		Un même tableau apparaît deux fois ou plus dans le fichier.

	Erreurs
	-------
	ParsingError
		Une métadonnée ou un entête est mal formé.
	ParsingError
		Les tableaux recherchés ne sont pas trouvés.
	TypeError
		Une métadonnée ou une valeur d'un tableau n'a pas le bon type.
	ValueError
		La valeur d'une métadata n'est pas supportée.
	"""
	if isinstance(fichier, (str, Path)) :
		with open(fichier, 'r') as f :
			return importer_vrp(f)


	métadonnées = dict()
	for ligne in fichier :
		if ligne == "\n" : break

		nom, valeur = extrait_métadonnée(ligne)

		typ = MÉTADONNÉE_CONNUES.get(nom)
		if typ is not None :
			try :
				valeur = typ(valeur)
			except Exception :
				raise TypeError(f"La métadonnée {{{nom!r} : {valeur!r}}} ne peut pas être converti en {typ.__name__}") from None

		métadonnées[nom] = valeur



	if (v := métadonnées.get("TYPE")) is not None and v != "vrptw" :
		raise ValueError(f"Type de données non supporté : \"{v}\" (attendu vrptw)")
	if (v := métadonnées.get("COORDINATES")) is not None and v != "cartesian" :
		raise ValueError(f"Type de coordonées non supporté : \"{v}\" (attendu cartesian)")



	contenu = dict()
	for ligne in fichier :

		nom, entête = extrait_entête(ligne)

		if nom in contenu :
			warnings.warn(f"Le tableau {nom} est présent deux fois dans le fichier. Seul le second sera pris en compte.")

		tableau = list()
		for ligne in fichier :
			if ligne == "\n" : break
			tableau.append(ligne.strip().split())

		contenu[nom] = entête, tableau



	entête, tableau = contenu.get("DATA_DEPOTS", (None,None))
	if entête is None :
		raise ParsingError("Le fichier .vrp ne contient aucune information sur le(s) dépôt(s) (habituellement dans le tableau DATA_DEPOTS)")
	ID, X, Y, DÉBUT_H, FIN_H = _cherche_entête(
		"DATA_DEPOTS",
		entête,
		["idName", "x", "y", "readyTime", "dueTime"]
	)
	dépots  = [ Client(
		ligne[ID],
		(int(ligne[X]), int(ligne[Y])),
		(int(ligne[DÉBUT_H]), int(ligne[FIN_H]))
	) for ligne in tableau ]



	entête, tableau = contenu.get("DATA_CLIENTS", (None,None))
	if entête is None :
		raise ParsingError("Le fichier .vrp ne contient aucune information sur les clients (habituellement dans le tableau DATA_CLIENTS)")
	ID, X, Y, DÉBUT_H, FIN_H, QUANT, DURÉE = _cherche_entête(
		"DATA_CLIENTS",
		entête,
		["idName", "x", "y", "readyTime", "dueTime", "demand", "service"]
	)
	clients = [ Client(
		ligne[ID],
		(int(ligne[X]), int(ligne[Y])),
		(int(ligne[DÉBUT_H]), int(ligne[FIN_H])),
		int(ligne[QUANT]),
		int(ligne[DURÉE])
	) for ligne in tableau ]



	return métadonnées, dépots, clients





def exporter_vrp(fichier :str|Path|IO[str], flotte :Flotte, **métadonnées :Any) :
	"""
	Exporte les données d'un objet Flotte dans un fichier .vrp.
	La fonction analyse les métadonnées, puis écrit les tableaux 'DATA_DEPOTS', 'DATA_TRAJETS', puis 'DATA_TRAJET_t...' pour chaque trajet.

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
			return exporter_vrp(f, flotte, **métadonnées)



	dépôts = {trajet.depot.id : trajet.depot for trajet in flotte.trajets}

	nb_dépôts  = len(dépôts)
	nb_trajets = flotte.nb_trajets
	nb_clients = sum(trajet.nb_clients for trajet in flotte.trajets)
	capacité   = flotte.capacite
	longueur   = flotte.longueur

	if (v := métadonnées.setdefault("NAME"        , ""         )) != ""         : pass
	if (v := métadonnées.setdefault("COMMENT"     , ""         )) != ""         : pass
	if (v := métadonnées.setdefault("TYPE"        , "vrptw"    )) != "vrptw"    : raise ValueError(f"Type de données non supporté : \"{v}\" (attendu vrptw)")
	if (v := métadonnées.setdefault("COORDINATES" , "cartesian")) != "cartesian": raise ValueError(f"Type de coordonées non supporté : \"{v}\" (attendu cartesian)")
	if (v := métadonnées.setdefault("NB_DEPOTS"   , nb_dépôts  )) != nb_dépôts  : raise ValueError(f"Incohérence dans le nombre de dépôts : résultat={nb_dépôts} métadonnées={v}")
	if (v := métadonnées.setdefault("NB_TRAJETS"  , nb_trajets )) != nb_trajets : raise ValueError(f"Incohérence dans le nombre de trajets : résultat={nb_trajets} métadonnées={v}")
	if (v := métadonnées.setdefault("NB_CLIENTS"  , nb_clients )) != nb_clients : raise ValueError(f"Incohérence dans le nombre de clients : résultat={nb_clients} métadonnées={v}")
	if (v := métadonnées.setdefault("MAX_QUANTITY", capacité   )) != capacité   : raise ValueError(f"Incohérence dans la capacité maximale des véhicules : résultat={capacité} métadonnées={v}")
	if (v := métadonnées.setdefault("LONGUEUR"    , longueur   )) != longueur   : raise ValueError(f"Incohérence dans la longueur totale : résultat={longueur} métadonnées={v}")



	for nom, valeur in métadonnées.items() :
		fichier.write(formate_métadonnée(nom, valeur))
	fichier.write("\n")



	fichier.write(formate_entête("DATA_DEPOTS", ["idName", "x", "y", "readyTime", "dueTime"]))
	for dépôt in dépôts.values() :
		ID = dépôt.id; X, Y = dépôt.pos; DÉBUT_H, FIN_H = dépôt.intervalle_livraison
		fichier.write(f"{ID}\t{X}\t{Y}\t{DÉBUT_H}\t{FIN_H}\n")
	fichier.write("\n")


	fichier.write(formate_entête("DATA_TRAJETS", ["idName", "distance", "quantity", "depot"]))
	for i, trajet in enumerate(flotte.trajets) :
		ID = f"t{i}"; DIST = trajet.longueur; QUANT = trajet.marchandise; DÉPOT = trajet.depot.id
		fichier.write(f"{ID}\t{DIST}\t{QUANT}\t{DÉPOT}\n")
	fichier.write("\n")


	for i, trajet in enumerate(flotte.trajets) :
		fichier.write(formate_entête(f"DATA_TRAJET_t{i}", ["idName", "x", "y", "readyTime", "dueTime", "demand", "service"]))
		for client in trajet.clients :
			ID = client.id; X, Y = client.pos; DÉBUT_H, FIN_H = client.intervalle_livraison; QUANT = client.demande; DURÉE = client.temps_livraison
			fichier.write(f"{ID}\t{X}\t{Y}\t{DÉBUT_H}\t{FIN_H}\t{QUANT}\t{DURÉE}\n")
		fichier.write("\n")
