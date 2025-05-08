from classes import Flotte, Trajet, distance, dist_echanger_tab_clients




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



def deux_opt(trajet :Trajet) -> tuple[float, tuple[int, int]] :
	"""
	Calcule et renvoie un tuple avec des informations sur le trajet avec la plus courte longueur 
	après une itération de 2-opt.
	
	Paramètres
	----------
	trajet : Trajet
		Trajet sur lequelle est appliqué l'opérateur 2-opt.
	
	Renvoie
	-------
	La différence de longueur entre le nouveau trajet et l'ancien, 
	et un tuple contenant les indices des segments modifiés.
	"""
	assert isinstance(trajet, Trajet)

	nb = trajet.nb_clients
	mini = 0
	ind = None
	for i in range(nb-1) :
		cli00 = trajet.clients[i-1] if i > 0 else trajet.depot
		cli01 = trajet.clients[i]
		dist_tmp = distance(cli00, cli01)
		for j in range(i+2, nb+1) :
			if i == 0 and j == nb: continue
			cli10 = trajet.clients[j-1] 
			cli11 = trajet.clients[j] if j < nb else trajet.depot
			dist = distance(cli00, cli10) + distance(cli01, cli11) - distance(cli10, cli11) - dist_tmp
			if dist < mini :
				mini = dist
				ind = (i, j)
	
	return (mini, ind)



def deux_opt_flotte(flotte :Trajet) -> tuple[float, tuple[int, int, int]] :
	"""
	Effectue l'opérateur 2-opt sur tous les trajets de la flotte et renvoie le meilleur.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur 2-opt.
	
	Renvoie
	-------
	La différence de longueur entre la nouvelle flotte et l'ancienne, et 
	un tuple contenant l'indice du trajet et les indices des segments modifiés.
	"""
	assert isinstance(flotte, Flotte)

	mini = 0
	ind = None
	for i, trajet in enumerate(flotte.trajets) :
		tmp = deux_opt(trajet)
		match tmp :
			case [float(dist), [int(x1), int(x2)]] :
				if dist < mini :
					mini = dist
					ind = (i, x1, x2)
			case _ :
				pass
	
	return (mini, ind)



def cross_exchange(flotte :Flotte) -> tuple[float, tuple[tuple[int, int], tuple[int, int]]] :
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
	un tuple de 2 tuples (indice trajet, indice dernier client) contenant les positions des derniers clients à échanger.
	"""
	assert isinstance(flotte, Flotte)

	mini = 0
	ind = None
	trajets = flotte.trajets
	for i, t1 in enumerate(trajets) :
		nb1 = t1.nb_clients
		clients1 = t1.clients
		for j in range(1, nb1) :
			marchandise1 = t1.info_marchandise_tab_clients(j)
			for x, t2 in enumerate(trajets[i+1:]) :
				nb2 = t2.nb_clients
				clients2 = t2.clients
				for y in range(1, nb2) :
					if j == nb1 - 1 and y == nb2 - 1: continue
					marchandise2 = t2.info_marchandise_tab_clients(y)
					if t1.marchandise - marchandise1 + marchandise2 <= flotte.capacite and t2.marchandise - marchandise2 + marchandise1 <= flotte.capacite :
						tmp = dist_echanger_tab_clients((t1, j), (t2, y))
						if tmp < mini :
							mini = tmp
							ind = ((i, j), (x+i+1, y))
	
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



def effectuer_cross_exchange(flotte :Flotte, new_dist :float, indice :tuple[tuple[int, int], tuple[int, int]]) :
	"""
	Effectue les changements en appliquant l'opérateur cross-exchange.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur cross-exchange.
	new_dist : float
		Différence de distance entre avant et après le changement.
	indice : tuple[tuple[int, int], tuple[int, int]]
		Indices des positions des derniers clients des listes à échanger.
	"""
	assert isinstance(flotte, Flotte)
	assert isinstance(new_dist, float) and new_dist < 0
	assert isinstance(indice, tuple)

	trajets = flotte.trajets
	flotte.longueur += new_dist
	match indice :
		case [[int(i), int(j)], [int(x), int(y)]] :
			tab_cli1 = trajets[i].retirer_tab_client(j)
			tab_cli2 = trajets[x].retirer_tab_client(y)
			trajets[x].ajouter_tab_client(tab_cli1)
			trajets[i].ajouter_tab_client(tab_cli2)
		case _ :
			raise AssertionError("Le paramètre indice ne respecte pas le bon format !")



def effectuer_2_opt(flotte :Flotte, new_dist :float, indice :tuple[int, int, int]) :
	"""
	Effectue les changements en appliquant l'opérateur 2-opt.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur 2-opt.
	new_dist : float
		Différence de distance entre avant et après le changement.
	indice : tuple[int, int, int]
		Indices des positions des segments à modifier.
	"""
	assert isinstance(flotte, Flotte)
	assert isinstance(new_dist, float) and new_dist < 0
	assert isinstance(indice, tuple)

	flotte.longueur += new_dist
	match indice :
		case [int(i), int(x1), int(x2)] :
			trajet = flotte.trajets[i]
			trajet.longueur += new_dist
			trajet.reverse_tab(x1, x2-1)
		case _ :
			raise AssertionError("Le paramètre indice ne respecte pas le bon format !")



def effectuer_changements(flotte :Flotte) -> bool :
	"""
	Applique l'opérateur le plus efficace.
	
	Paramètres
	----------
	flotte : Flotte
		Flotte sur laquelle est appliqué l'opérateur.
	
	Renvoie
	-------
	False si aucun opérateur ne permet d'améliorer le trajet, True sinon.
	"""
	assert isinstance(flotte, Flotte)
	
	exchange = inter_exchange(flotte)
	relocate = inter_relocate(flotte)
	cross_exch = cross_exchange(flotte)
	deux_opt = deux_opt_flotte(flotte)
	
	match [relocate[1], exchange[1], cross_exch[1], deux_opt[1]] :
		case [None, None, None, None] :
			return False
		case [ind_relocate, None, None, None] :
			effectuer_relocate(flotte, relocate[0], ind_relocate)
		case [None, ind_exchange, None, None] :
			effectuer_exchange(flotte, exchange[0], ind_exchange)
		case [None, None, ind_cross_exch, None] :
			effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
		case [ind_relocate, ind_exchange, None, None] :
			if relocate[0] < exchange[0] : effectuer_relocate(flotte, relocate[0], ind_relocate)
			else : effectuer_exchange(flotte, exchange[0], ind_exchange)
		case [ind_relocate, None, ind_cross_exch, None] :
			if relocate[0] < cross_exch[0] : effectuer_relocate(flotte, relocate[0], ind_relocate)
			else : effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
		case [None, ind_exchange, ind_cross_exch, None] :
			if exchange[0] < cross_exch[0] : effectuer_exchange(flotte, exchange[0], ind_exchange)
			else : effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
		case [ind_relocate, ind_exchange, ind_cross_exch, None] :
			if relocate[0] < exchange[0] and relocate[0] < cross_exch[0] : effectuer_relocate(flotte, relocate[0], ind_relocate)
			elif exchange[0] < cross_exch[0] : effectuer_exchange(flotte, exchange[0], ind_exchange)
			else : effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
		
		case [None, None, None, ind_2_opt] :
			effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
		
		case [ind_relocate, None, None, ind_2_opt] :
			if relocate[0] < deux_opt[0] : effectuer_relocate(flotte, relocate[0], ind_relocate)
			else : effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
		case [None, ind_exchange, None, ind_2_opt] :
			if exchange[0] < deux_opt[0] : effectuer_exchange(flotte, exchange[0], ind_exchange)
			else : effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
		case [None, None, ind_cross_exch, ind_2_opt] :
			if cross_exch[0] < deux_opt[0] : effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
			else : effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
		
		case [ind_relocate, ind_exchange, None, ind_2_opt] :
			if relocate[0] < exchange[0] and relocate[0] < deux_opt[0] : effectuer_relocate(flotte, relocate[0], ind_relocate)
			elif exchange[0] < deux_opt[0] : effectuer_exchange(flotte, exchange[0], ind_exchange)
			else : effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
		case [ind_relocate, None, ind_cross_exch, ind_2_opt] :
			if relocate[0] < deux_opt[0] and relocate[0] < cross_exch[0] : effectuer_relocate(flotte, relocate[0], ind_relocate)
			elif deux_opt[0] < cross_exch[0] : effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
			else : effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
		case [None, ind_exchange, ind_cross_exch, ind_2_opt] :
			if deux_opt[0] < exchange[0] and deux_opt[0] < cross_exch[0] : effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
			elif exchange[0] < cross_exch[0] : effectuer_exchange(flotte, exchange[0], ind_exchange)
			else : effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
		
		case [ind_relocate, ind_exchange, ind_cross_exch, ind_2_opt] :
			if relocate[0] < exchange[0] and relocate[0] < cross_exch[0] and relocate[0] < deux_opt[0] : effectuer_relocate(flotte, relocate[0], ind_relocate)
			elif exchange[0] < cross_exch[0] and exchange[0] < deux_opt[0] : effectuer_exchange(flotte, exchange[0], ind_exchange)
			elif deux_opt[0] < cross_exch[0] : effectuer_2_opt(flotte, deux_opt[0], ind_2_opt)
			else : effectuer_cross_exchange(flotte, cross_exch[0], ind_cross_exch)
	
	return True