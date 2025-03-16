from classes import Flotte, Trajet, distance




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

	nb = trajet.nb_clients
	mini = 0
	ind = None
	
	for i in range(nb) :
		cli = trajet.clients[i]
		dist_tmp = trajet.dist_retirer_client(i)
		for j in range(nb+1) :
			if j == i or j == i+1 : continue

			dist_tmp2 = dist_tmp + trajet.dist_ajouter_client(j, cli)

			if dist_tmp2 < mini:
				mini = dist_tmp
				ind = (i, j if j < i else j-1)
	
	return (mini, ind)



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
	for i, t1 in enumerate(trajets) :
		for x, t2 in enumerate(trajets) :
			if x == i :
				min_tmp, ind_tmp = intra_relocate(trajets[x])
				if min_tmp < mini : 
					ind = ((i, ind_tmp[0]), (x, ind_tmp[1]))
					mini = min_tmp
			else :
				for j, c in enumerate(t1.clients) :
					tmp = t1.dist_retirer_client(j)
					for y in range(t2.nb_clients+1) :
						if t2.marchandise + c.demande <= flotte.capacite :
							tmp2 = tmp + t2.dist_ajouter_client(y, c)
							if tmp2 < mini :
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
			if tmp < mini :
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
	for i, t1 in enumerate(trajets) :
		for x, t2 in enumerate(trajets[i:]) :
			if x == 0 :
				min_tmp, ind_tmp = intra_exchange(trajets[i])
				if min_tmp < mini : 
					ind = ((i, ind_tmp[0]), (i, ind_tmp[1]))
					mini = min_tmp
			else :
				for j, c1 in enumerate(t1.clients) :
					for y, c2 in enumerate(t2.clients) :
						if t1.marchandise - c1.demande + c2.demande <= flotte.capacite and t2.marchandise - c2.demande + c1.demande <= flotte.capacite :
							tmp = t1.dist_remplacer_client(j, c2) + t2.dist_remplacer_client(y, c1)
							if tmp < mini :
								mini = tmp
								ind = ((i, j), (x+i, y))
	
	return (mini, ind)



def cross_exchange(flotte :Flotte) -> tuple[float, tuple[tuple[int, int, int], tuple[int, int, int]]] :
	"""
	Calcule et renvoie un tuple avec des informations sur la flotte avec la plus courte longueur 
	après une itération de cross-exchange.

	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur cross-exchange.

	Renvoie
	-------
	La différence de longueur entre la nouvelle flotte et l'ancienne, et 
	un tuple de 2 tuples (indice trajet, indice premier client, indice dernier client) contenant les positions des clients échangés.
	"""
	assert isinstance(flotte, Flotte)

	mini = 0
	ind = None
	trajets = flotte.trajets
	for i, t1 in enumerate(trajets) :
		nb1 = t1.nb_clients
		clients1 = t1.clients
		for j in range(1, nb1) :
			tab_cli1 = t1.info_tab_clients(0, j)
			for x, t2 in enumerate(trajets[i+1:]) :
				nb2 = t2.nb_clients
				clients2 = t2.clients
				for y in range(1, nb2) :
					if j == nb1 - 1 and y == nb2 - 1: continue
					tab_cli2 = t2.info_tab_clients(0, y)
					if t1.marchandise - tab_cli1[1] + tab_cli2[1] <= flotte.capacite and t2.marchandise - tab_cli2[1] + tab_cli1[1] <= flotte.capacite :
						tmp = t1.dist_remplacer_tab_client(0, j, clients2[0], clients2[y], tab_cli2[0])
						tmp += t2.dist_remplacer_tab_client(0, y, clients1[0], clients1[j], tab_cli1[0])
						if tmp < mini :
							mini = tmp
							ind = ((i, 0, j), (x+i+1, 0, y))
	
	return (mini, ind)



def effectuer_relocate(flotte :Flotte, new_dist :float, indice :tuple[tuple[int, int], tuple[int, int]]) :
	"""
	Effectue les changements en appliquant l'opérateur relocate.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur relocate.
	new_dist : float
		Différence de distance entre avant et après le changement.
	indice : tuple[tuple[int, int], tuple[int, int]]
		Indices de la position initiale et finale.
	"""
	assert isinstance(flotte, Flotte)
	assert isinstance(new_dist, float) and new_dist < 0
	assert isinstance(indice, tuple)

	trajets = flotte.trajets
	flotte.longueur += new_dist
	match indice :
		case [[int(i), int(j)], [int(x), int(y)]] :
			cli = trajets[i].retirer_client(j)
			trajets[x].ajouter_client(y, cli)
			if trajets[i].nb_clients == 0: flotte.retirer_trajet(i)
		case _ :
			raise AssertionError("Le paramètre indice ne respecte pas le bon format !")



def effectuer_exchange(flotte :Flotte, new_dist :float, indice :tuple[tuple[int, int], tuple[int, int]]) :
	"""
	Effectue les changements en appliquant l'opérateur exchange.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur exchange.
	new_dist : float
		Différence de distance entre avant et après le changement.
	indice : tuple[tuple[int, int], tuple[int, int]]
		Indices des positions des clients à échanger.
	"""
	assert isinstance(flotte, Flotte)
	assert isinstance(new_dist, float) and new_dist < 0
	assert isinstance(indice, tuple)

	trajets = flotte.trajets
	flotte.longueur += new_dist
	match indice :
		case [[int(i), int(j)], [int(x), int(y)]] :
			cli1 = trajets[i].clients[j]
			cli2 = trajets[x].retirer_client(y)
			trajets[x].ajouter_client(y, cli1)
			trajets[i].retirer_client(j)
			trajets[i].ajouter_client(j, cli2)
		case _ :
			raise AssertionError("Le paramètre indice ne respecte pas le bon format !")



def effectuer_cross_exchange(flotte :Flotte, new_dist :float, indice :tuple[tuple[int, int, int], tuple[int, int, int]]) :
	"""
	Effectue les changements en appliquant l'opérateur cross-exchange.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur cross-exchange.
	new_dist : float
		Différence de distance entre avant et après le changement.
	indice : tuple[tuple[int, int, int], tuple[int, int, int]]
		Indices des positions des premiers et derniers clients des listes à échanger.
	"""
	assert isinstance(flotte, Flotte)
	assert isinstance(new_dist, float) and new_dist < 0
	assert isinstance(indice, tuple)

	trajets = flotte.trajets
	flotte.longueur += new_dist
	match indice :
		case [[int(i), int(j), int(k)], [int(x), int(y), int(z)]] :
			tab_cli1 = trajets[i].retirer_tab_client(j, k)
			tab_cli2 = trajets[x].retirer_tab_client(y, z)
			trajets[x].ajouter_tab_client(y, tab_cli1)
			trajets[i].ajouter_tab_client(j, tab_cli2)
		case _ :
			raise AssertionError("Le paramètre indice ne respecte pas le bon format !")
	


def cross_exchange2(flotte :Flotte) -> tuple[float, tuple[tuple[int, int, int], tuple[int, int, int]]] :
	"""
	Calcule et renvoie un tuple avec des informations sur la flotte avec la plus courte longueur 
	après une itération de cross-exchange.

	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur cross-exchange.

	Renvoie
	-------
	La différence de longueur entre la nouvelle flotte et l'ancienne, et 
	un tuple de 2 tuples (indice trajet, indice premier client, indice dernier client) contenant les positions des clients échangés.
	"""
	assert isinstance(flotte, Flotte)

	mini = 0
	ind = None
	trajets = flotte.trajets
	for i, t1 in enumerate(trajets) :
		nb1 = t1.nb_clients
		clients1 = t1.clients
		for j in range(nb1-1) :
			for k in range(j+1, nb1) :
				tab_cli1 = t1.info_tab_clients(j, k)
				for x, t2 in enumerate(trajets[i+1:]) :
					nb2 = t2.nb_clients
					clients2 = t2.clients
					for y in range(nb2-1) :
						for z in range(y+1, nb2) :
							if j == y == 0 and k == nb1 - 1 and z == nb2 - 1: continue
							tab_cli2 = t2.info_tab_clients(y, z)
							if t1.marchandise - tab_cli1[1] + tab_cli2[1] <= flotte.capacite and t2.marchandise - tab_cli2[1] + tab_cli1[1] <= flotte.capacite :
								tmp = t1.dist_remplacer_tab_client(j, k, clients2[y], clients2[z], tab_cli2[0])
								tmp += t2.dist_remplacer_tab_client(y, z, clients1[j], clients1[k], tab_cli1[0])
								if tmp < mini :
									mini = tmp
									ind = ((i, j, k), (x+i+1, y, z))
	
	return (mini, ind)
