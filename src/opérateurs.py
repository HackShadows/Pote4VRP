from classes import Flotte, Trajet, distance

from itertools import islice





def intra_relocate(trajet :Trajet) -> tuple[float, tuple[int, int]] :
	"""
	Calcule et renvoie un tuple avec des informations sur le trajet avec la plus courte longueur 
	après une itération de relocate.
	
	Paramètres
	----------
	trajet : Trajet
		Trajet sur lequelle est appliqué l'opérateur relocate.
	
	Renvoie
	-------
	La différence de longueur entre le nouveau trajet et l'ancien, et 
	un tuple contenant la position originale et la nouvelle position du client relocalisé.
	"""
	assert isinstance(trajet, Trajet)

	lg = trajet.longueur
	nb = trajet.nb_clients
	mini = trajet.longueur
	ind = None
	for i in range(nb) :
		#TODO: pas besoin d'appeler retirer et ajouter, on peut garder une trace de la longeur du trajet avec lg
		cli = trajet.retirer_client(i)
		tmp = trajet.longueur
		#TODO: plus rapide ?
		# j, m = min(enumerate(map(trajet.dist_ajouter_client, range(nb), cli)), key=lambda v: v[1])
		# if m < mini :
		# 	mini = m
		# 	ind = (i, j)
		for j in range(nb) :
			if i == j : continue

			tmp2 = tmp + trajet.dist_ajouter_client(j, cli)
			#if tmp2 <= mini and j != i:
			if tmp2 < mini:
				#print("Indices : ", ind, " ; Mini : ", mini, " ; tmp : ", tmp2)
				mini = tmp2
				ind = (i, j)
		trajet.ajouter_client(i, cli)
	return (mini - lg, ind)



def inter_relocate(flotte :Flotte) -> tuple[float, tuple[tuple[int, int], tuple[int, int]]] :
	"""
	Calcule et renvoie un tuple avec des informations sur la flotte avec la plus courte longueur 
	après une itération de relocate.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur relocate.
	
	Renvoie
	-------
	La différence de longueur entre la nouvelle flotte et l'ancienne, et 
	un tuple de 2 tuples (indice trajet, indice client) contenant la position originale 
	et la nouvelle position du client relocalisé.
	"""
	assert isinstance(flotte, Flotte)

	mini = 0
	ind = None
	trajets = flotte.trajets
	for i, t in enumerate(trajets) : #TODO: i et x ???, t et t2 ???
		for x, t2 in enumerate(trajets) :
			if x == i :
				#print("Intra relocate : ")
				min_tmp, ind_tmp = intra_relocate(trajets[x])
				#if ind_tmp != None and min_tmp <= mini: 
				if min_tmp < mini : 
					ind = ((i, ind_tmp[0]), (x, ind_tmp[1]))
					mini = min_tmp
			else :
				#print("Inter relocate : ")
				for j, c in enumerate(t.clients) :
					tmp = t.dist_retirer_client(j)
					for y in range(t2.nb_clients+1) :
						if t2.marchandise + c.demande <= flotte.capacite :
							tmp2 = tmp + t2.dist_ajouter_client(y, c)
							#if tmp2 <= mini:
							if tmp2 < mini :
								#print("Indices : ", ind, " ; Mini : ", mini, " ; tmp : ", tmp2)
								mini = tmp2
								ind = ((i, j), (x, y))
	return (mini, ind)



def intra_exchange(trajet :Trajet) -> tuple[float, tuple[int, int]] :
	"""
	Calcule et renvoie un tuple avec des informations sur le trajet avec la plus courte longueur 
	après une itération de exchange.
	
	Paramètres
	----------
	trajet : Trajet
		Trajet sur lequelle est appliqué l'opérateur exchange.
	
	Renvoie
	-------
	La différence de longueur entre le nouveau trajet et l'ancien, 
	et un tuple contenant les positions des clients échangés.
	"""
	assert isinstance(trajet, Trajet)
	
	nb = trajet.nb_clients
	mini = 0
	ind = None
	for i in range(nb-1) :
		cli = trajet.clients[i]
		cli_tmp = trajet.clients[i+1]
		tmp = trajet.dist_remplacer_client(i, cli_tmp) + trajet.dist_remplacer_client(i+1, cli) + 3*distance(cli, cli_tmp)
		if tmp < mini :
			mini = tmp
			ind = (i, i+1)
		for j in range(i+2, nb) :
			tmp = trajet.dist_remplacer_client(i, trajet.clients[j]) + trajet.dist_remplacer_client(j, cli)
			#if tmp <= mini and j != i:
			if tmp < mini :
				#print("Indices : ", ind, " ; Mini : ", mini, " ; tmp : ", tmp)
				mini = tmp
				ind = (i, j)
	return (mini, ind)



def inter_exchange(flotte :Flotte) -> tuple[float, tuple[tuple[int, int], tuple[int, int]]] :
	"""
	Calcule et renvoie un tuple avec des informations sur la flotte avec la plus courte longueur 
	après une itération de exchange.

	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur exchange.

	Renvoie
	-------
	La différence de longueur entre la nouvelle flotte et l'ancienne, et 
	un tuple de 2 tuples (indice trajet, indice client) contenant les positions des clients échangés.
	"""
	assert isinstance(flotte, Flotte)

	mini = 0
	ind = None
	trajets = flotte.trajets
	for i, t in enumerate(trajets) :
		for x, t2 in enumerate(trajets[i:]) :#islice(trajets, i, len(trajets))) :
			if x == 0:
				#print("Intra exchange : ")
				min_tmp, ind_tmp = intra_exchange(trajets[i])
				#if ind_tmp != None and min_tmp <= mini: 
				if min_tmp < mini: 
					ind = ((i, ind_tmp[0]), (i, ind_tmp[1]))
					mini = min_tmp
			else:
				#print("Inter exchange : ")
				for j, c in enumerate(t.clients):
					for y, c2 in enumerate(t2.clients) :
						if t.marchandise - c.demande + c2.demande <= flotte.capacite and t2.marchandise - c2.demande + c.demande <= flotte.capacite :
							tmp = t.dist_remplacer_client(j, c2) + t2.dist_remplacer_client(y, c)
							#if tmp <= mini:
							if tmp < mini :
								#print("Indices : ", ind, " ; Mini : ", mini, " ; tmp : ", tmp)
								mini = tmp
								ind = ((i, j), (x+i, y))
	return (mini, ind)



def cross_exchange(flotte :Flotte) -> tuple:
	"""
	Calcule et renvoie un tuple avec des informations sur la flotte avec la plus courte longueur 
	après une itération de exchange.

	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur exchange.

	Renvoie
	-------
	La différence de longueur entre la nouvelle flotte et l'ancienne, et 
	un tuple de 2 tuples (indice trajet, indice client) contenant les positions des clients échangés.
	"""
	assert isinstance(flotte, Flotte)

	mini = 0
	ind = None
	trajets = flotte.trajets
	for i, t in enumerate(trajets) :
		for x, t2 in enumerate(trajets[i:]) :#islice(trajets, i, len(trajets))) :
			if x == 0:
				#print("Intra exchange : ")
				min_tmp, ind_tmp = intra_exchange(trajets[i])
				#if ind_tmp != None and min_tmp <= mini: 
				if min_tmp < mini: 
					ind = ((i, ind_tmp[0]), (i, ind_tmp[1]))
					mini = min_tmp
			else:
				#print("Inter exchange : ")
				for j, c in enumerate(t.clients):
					for y, c2 in enumerate(t2.clients) :
						if t.marchandise - c.demande + c2.demande <= flotte.capacite and t2.marchandise - c2.demande + c.demande <= flotte.capacite :
							tmp = t.dist_remplacer_client(j, c2) + t2.dist_remplacer_client(y, c)
							#if tmp <= mini:
							if tmp < mini :
								#print("Indices : ", ind, " ; Mini : ", mini, " ; tmp : ", tmp)
								mini = tmp
								ind = ((i, j), (x+i, y))
	return (mini, ind)



def effectuer_changements(flotte :Flotte, new_dist :float, indice :tuple[tuple[int, int], tuple[int, int]], action :int) :
	"""
	Calcule et renvoie un tuple avec des informations sur la flotte avec la plus courte longueur 
	après une itération de exchange.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué le changement 'action'.
	new_dist : float
		Différence de distance entre avant et après le changement.
	indice : tuple[tuple[int, int], tuple[int, int]]
		Indices des deux positions sur lesquelles le changements est effectué.
	action : int
		Opérateur utilisé pour le changement (1 = relocate, 2 = exchange).
	"""
	(i, j), (x, y) = indice
	trajets = flotte.trajets
	flotte.longueur += new_dist
	match action :
		case 1 :
			cli = trajets[i].retirer_client(j)
			trajets[x].ajouter_client(y, cli)
			if trajets[i].nb_clients == 0: flotte.retirer_trajet(i)
		case 2 :
			cli = trajets[i].clients[j]
			cli2 = trajets[x].retirer_client(y)
			trajets[x].ajouter_client(y, cli)
			trajets[i].retirer_client(j)
			trajets[i].ajouter_client(j, cli2)
