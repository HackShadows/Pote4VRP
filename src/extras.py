from classes import Client, Trajet, Flotte, distance

class Trajet :
	
	# dist_ajouter_tab_client jamais utilisée
	def dist_ajouter_tab_client(self, indice :int, cli_debut :Client, cli_fin :Client, lg_tab :int) -> float :
		"""
		Calcule et renvoie la différence de distance entre avant et après l'ajout de la liste de clients.

		Paramètres
		----------
		indice : int
			Indice où insérer la liste de clients.
		cli_debut : Client
			Premier client de la liste.
		cli_fin : Client
			Dernier client de la liste.
		lg_tab : int
			Longueur du trajet entre le premier et le dernier client.

		Renvoie
		-------
		La différence positive de distance entre avant et après l'ajout de la liste de clients.
		"""
		assert isinstance(cli_debut, Client) and isinstance(cli_fin, Client)
		assert isinstance(indice, int) and 0 <= indice
		assert isinstance(lg_tab, int) and 0 < lg_tab

		if self.nb_clients == 0 :
			cli0 = self.depot
			cli1 = self.depot
		elif indice == 0 :
			cli0 = self.depot
			cli1 = self.clients[0]
		elif indice >= self.nb_clients :
			cli0 = self.clients[-1]
			cli1 = self.depot
		else :
			cli0 = self.clients[indice-1]
			cli1 = self.clients[indice]

		return distance(cli0, cli_debut) + lg_tab + distance(cli_fin, cli1) - distance(cli0, cli1)
	


	def info_tab_clients(self, ind_debut :int, ind_fin :int) -> tuple[float, int] :
		"""
		Calcule et renvoie la distance et la marchandise du trajet située entre les indices passés en paramètre.

		Paramètres
		----------
		ind_debut : int
			Indice du premier client.
		ind_fin : int
			Indice du dernier client.

		Renvoie
		-------
		La distance et la marchandise du trajet situé entre le premier et le dernier client.
		"""
		assert isinstance(ind_debut, int) and isinstance(ind_fin, int)
		assert 0 <= ind_debut < ind_fin < self.nb_clients

		dist = 0
		marchandise = 0
		for i in range(ind_debut, ind_fin) :
			cli = self.clients[i]
			marchandise += cli.demande
			dist += distance(cli, self.clients[i+1])
		marchandise += self.clients[ind_fin].demande
		
		return (dist, marchandise)



	def dist_retirer_tab_client(self, ind_debut :int, ind_fin :int) -> float :
		"""
		Calcule et renvoie la différence de distance entre avant et après 
		le retrait des clients situés entre les 2 indices.

		Paramètres
		----------
		ind_debut : int
			Indice du premier client.
		ind_fin : int
			Indice du dernier client.

		Renvoie
		-------
		La différence négative de distance entre avant et après le retrait des clients.
		"""
		assert isinstance(ind_debut, int) and isinstance(ind_fin, int)
		assert 0 <= ind_debut < ind_fin < self.nb_clients

		infos = self.info_tab_clients(ind_debut, ind_fin)
		cli0 = self.depot if ind_debut == 0                 else self.clients[ind_debut-1]
		cli1 = self.depot if ind_fin == self.nb_clients - 1 else self.clients[ind_fin+1]

		return distance(cli0, cli1) - distance(cli0, self.clients[ind_debut]) - distance(self.clients[ind_fin], cli1) - infos[0]



	def dist_remplacer_tab_client(self, ind_debut :int, ind_fin :int, cli_debut :Client, cli_fin :Client, lg_tab :float) -> float :
		"""
		Calcule et renvoie la différence de distance entre avant et après le remplacement de la liste de clients.

		Paramètres
		----------
		ind_debut : int
			Indice du premier client de la liste à remplacer.
		ind_fin : int
			Indice du dernier client de la liste à remplacer.
		cli_debut : Client
			Premier client de la liste à ajouter.
		cli_fin : Client
			Dernier client de la liste à ajouter.
		lg_tab : int
			Longueur du trajet entre le premier et le dernier client à ajouter.

		Renvoie
		-------
		La différence de distance entre avant et après le remplacement de la liste de clients.
		"""
		assert isinstance(cli_debut, Client) and isinstance(cli_fin, Client)
		assert isinstance(ind_debut, int) and isinstance(ind_fin, int) and 0 <= ind_debut < ind_fin < self.nb_clients
		assert isinstance(lg_tab, float) and 0 < lg_tab

		dist_retirer_tab_client = self.dist_retirer_tab_client(ind_debut, ind_fin)
		cli0 = self.depot if ind_debut == 0                 else self.clients[ind_debut-1]
		cli1 = self.depot if ind_fin == self.nb_clients - 1 else self.clients[ind_fin+1]

		return distance(cli0, cli_debut) + lg_tab + distance(cli_fin, cli1) + dist_retirer_tab_client



	def ajouter_tab_client(self, indice :int, tab_clients :list[Client]) :
		"""
		Ajoute une liste de clients à la feuille de route, à la position 'indice'.

		Paramètres
		----------
		indice : int
			Indice où insérer la liste de clients.
		tab_clients : list[Client]
			Liste ordonnée des clients à ajouter dans l'itinéraire de livraison.
		"""
		assert isinstance(tab_clients, list)
		assert isinstance(indice, int) and indice >= 0

		for client in tab_clients[::-1]:
			assert isinstance(client, Client)
			self.ajouter_client(indice, client)



	def retirer_tab_client(self, ind_debut :int, ind_fin :int) -> list[Client] :
		"""
		Retire une liste de clients consécutifs de l'itinéraire.

		Paramètres
		----------
		ind_debut : int
			Indice du premier client.
		ind_fin : int
			Indice du dernier client.

		Renvoie
		-------
		La liste ordonnée des clients retirés du trajet.
		"""
		assert isinstance(ind_debut, int) and isinstance(ind_fin, int)
		assert 0 <= ind_debut < ind_fin < self.nb_clients

		liste_clients = []
		for _ in range(ind_fin - ind_debut + 1):
			liste_clients.append(self.retirer_client(ind_debut))
		
		return liste_clients



# Opérateurs

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
