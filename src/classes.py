from math import sqrt





class Client :

	__slots__ = "id", "pos", "demande", "intervalle_livraison", "temps_livraison"

	def __init__(self, id_ :str = "-1", pos :tuple[int, int] = (0, 0), intervalle_livraison :tuple[int, int] = (-1, -1), demande :int = 0, temps_livraison :int = 0) :
		self.id = id_
		self.pos = pos
		self.demande = demande
		self.intervalle_livraison = intervalle_livraison
		self.temps_livraison = temps_livraison


	def __repr__(self) -> str :
		x, y = self.pos
		return f"Client(id: {self.id}, position: ({x} {y}))"
	

	def afficher(self) :
		"""
		Affiche les informations détaillées du client.
		"""
		x, y = self.pos
		début, fin = self.intervalle_livraison
		temps = self.temps_livraison
		print(f"Client(id: {self.id}, position: ({x} {y}), livraison entre {début} et {fin}, demande: {self.demande}, temps de livraison: {temps})")



def distance(client1 :Client, client2 :Client) -> float :
	x1, y1 = client1.pos
	x2, y2 = client2.pos
	return sqrt((x2 - x1)**2 + (y2 - y1)**2)





class Trajet :

	__slots__ = "longueur", "nb_clients", "clients", "depot", "marchandise", "horaires"

	def __init__(self, depot :Client = Client()) :
		self.longueur = 0.0
		self.nb_clients = 0
		self.clients = []
		self.depot = depot
		self.marchandise = 0
		self.horaires = []


	def __repr__(self) -> str :
		long = self.longueur
		nb = self.nb_clients
		return f"Trajet(longueur : {long:.2f}km, contient {nb} clients)"
	
	
	def afficher(self, affichage :bool = False) :
		"""
		Affiche la longueur et le nombre de clients du trajet.
		Affiche en plus les horaires de livraison si affichage = True, 
		la liste ordonnée des clients du trajet sinon.

		Paramètres
		----------
		affichage : bool
			Booléen permettant de préciser l'affichage.
		"""
		long = self.longueur
		nb = self.nb_clients
		print(f"Trajet(longueur : {long:.2f}km, contient {nb} clients, {self.horaires if affichage else [c.id for c in self.clients]})")



	def ajouter_client(self, indice :int, client :Client) :
		"""
		Ajoute un client à la feuille de route, à la position 'indice'.

		Paramètres
		----------
		indice : int
			Indice où insérer le client.
		client : Client
			Client à ajouter dans l'itinéraire de livraison.
		"""
		assert isinstance(client, Client)
		assert isinstance(indice, int) and 0 <= indice

		self.longueur += self.dist_ajouter_client(indice, client)
		self.marchandise += client.demande
		if indice >= self.nb_clients: self.maj_horaires([client])
		else: 
			self.horaires = self.horaires[:indice]
			self.maj_horaires([client] + self.clients[indice:])
		self.clients.insert(indice, client)
		self.nb_clients += 1



	def retirer_client(self, indice :int) -> Client :
		"""
		Retire un client de l'itinéraire.

		Paramètres
		----------
		indice : int
			Indice du client dans la liste non vide 'clients'.

		Renvoie
		-------
		Le client se trouvant à l'indice passé en paramètre.
		"""
		assert isinstance(indice, int) and 0 <= indice < self.nb_clients

		self.longueur += self.dist_retirer_client(indice)
		cli = self.clients.pop(indice)
		self.nb_clients -= 1
		self.marchandise -= cli.demande
		if indice == self.nb_clients: self.horaires.pop(indice)
		else:
			self.horaires = self.horaires[:indice]
			self.maj_horaires(self.clients[indice:])
		return cli



	def dist_ajouter_client(self, indice :int, client :Client) -> float :
		"""
		Calcule et renvoie la différence de distance entre avant et après l'ajout du client.

		Paramètres
		----------
		indice : int
			Indice du client dans la liste 'clients'.
		client : Client
			Client à ajouter dans l'itinéraire de livraison.

		Renvoie
		-------
		La différence positive de distance entre avant et après l'ajout du client.
		"""
		assert isinstance(client, Client)
		assert isinstance(indice, int) and indice >= 0

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

		return distance(cli0, client) + distance(cli1, client) - distance(cli0, cli1)



	def dist_retirer_client(self, indice :int) -> float :
		"""
		Calcule et renvoie la différence de distance entre avant et après le retrait du client.

		Paramètres
		----------
		indice : int
			Indice du client dans la liste non vide 'clients'.

		Renvoie
		-------
		La différence négative de distance entre avant et après le retrait du client.
		"""
		assert isinstance(indice, int) and 0 <= indice < self.nb_clients

		client = self.clients[indice]
		if self.nb_clients == 1 :
			cli0 = self.depot
			cli1 = self.depot
		elif indice == 0 :
			cli0 = self.depot
			cli1 = self.clients[1]
		elif indice == self.nb_clients - 1 :
			cli0 = self.clients[-2]
			cli1 = self.depot
		else :
			cli0 = self.clients[indice-1]
			cli1 = self.clients[indice+1]

		return distance(cli0, cli1) - distance(cli0, client) - distance(client, cli1)



	def dist_remplacer_client(self, indice :int, nouveau :Client) -> float :
		"""
		Calcule et renvoie la différence de distance entre avant et après le remplacement du client.

		Paramètres
		----------
		indice : int
			Indice du client à remplacer dans la liste non vide 'clients'.
		nouveau : Client
			Client utilisé pour le remplacement.

		Renvoie
		-------
		La différence de distance entre avant et après le remplacement du client.
		"""
		assert isinstance(nouveau, Client)
		assert isinstance(indice, int) and 0 <= indice < self.nb_clients

		vieux = self.clients[indice]
		if self.nb_clients == 1 :
			cli0 = self.depot
			cli1 = self.depot
		elif indice == 0 :
			cli0 = self.depot
			cli1 = self.clients[1]
		elif indice == self.nb_clients-1 :
			cli0 = self.clients[-2]
			cli1 = self.depot
		else :
			cli0 = self.clients[indice-1]
			cli1 = self.clients[indice+1]

		return distance(cli0, nouveau) + distance(nouveau, cli1) - distance(cli0, vieux) - distance(vieux, cli1)



	def reverse_tab(self, ind_debut :int, ind_fin :int) :
		"""
		Inverse le tableau de clients entre les indices 'ind_debut' et 'ind_fin' inclus.

		Paramètres
		----------
		ind_debut : int
			Indice du premier client.
		ind_fin : int
			Indice du dernier client.
		"""
		assert isinstance(ind_debut, int) and isinstance(ind_fin, int) and 0 <= ind_debut <= ind_fin < self.nb_clients
		
		clients = self.clients
		for i in range((ind_fin - ind_debut + 1)//2):
			cli_tmp = clients[ind_debut+i]
			clients[ind_debut+i] = clients[ind_fin-i]
			clients[ind_fin-i] = cli_tmp
			


	def info_marchandise_tab_clients(self, indice :int) -> int :
		"""
		Calcule et renvoie la marchandise du trajet jusqu'à 'indice' inclus.

		Paramètres
		----------
		indice : int
			Indice du dernier client.

		Renvoie
		-------
		La marchandise du trajet jusqu'à 'indice' inclus.
		"""
		assert isinstance(indice, int) and 1 <= indice < self.nb_clients

		marchandise = 0
		for i in range(indice) :
			cli = self.clients[i]
			marchandise += cli.demande
		marchandise += self.clients[indice].demande
		
		return marchandise



	def ajouter_tab_client(self, tab_clients :list[Client]) :
		"""
		Ajoute une liste de clients au début de la feuille de route.

		Paramètres
		----------
		tab_clients : list[Client]
			Liste ordonnée des clients à ajouter dans l'itinéraire de livraison.
		"""
		assert isinstance(tab_clients, list)

		for client in tab_clients[::-1] :
			assert isinstance(client, Client)
			self.ajouter_client(0, client)



	def retirer_tab_client(self, indice :int) -> list[Client] :
		"""
		Retire une liste de clients consécutifs de l'itinéraire.

		Paramètres
		----------
		indice : int
			Indice du dernier client.

		Renvoie
		-------
		La liste ordonnée des clients retirés du trajet.
		"""
		assert isinstance(indice, int)
		assert 1 <= indice < self.nb_clients

		liste_clients = []
		for _ in range(indice + 1) :
			liste_clients.append(self.retirer_client(0))
		
		return liste_clients



	def maj_horaires(self, clients :list[Client]) :
		"""
		Ajoute les horaires de livraison des clients de 'clients' aux horaires déjà existantes.

		Paramètres
		----------
		clients : list[Client]
			Liste des clients à ajouter.
		"""
		assert isinstance(clients, list)

		for client in clients:
			assert isinstance(client, Client)
			if len(self.horaires) == 0 or self.horaires[-1] <= client.intervalle_livraison[0]: self.horaires.append(client.intervalle_livraison[0] + client.temps_livraison)
			else: self.horaires.append(self.horaires[-1] + client.temps_livraison)



def dist_echanger_tab_clients(trajet1 :tuple[Trajet, int], trajet2 :tuple[Trajet, int]) -> float :
	"""
	Calcule et renvoie la différence de distance entre avant et après l'échange des portions de trajets.

	Paramètres
	----------
	trajet1 : tuple[Trajet, int]
		Tuple contenant le premier trajet et l'indice où effectuer la séparation.
	trajet2 : tuple[Trajet, int]
		Tuple contenant le second trajet et l'indice où effectuer la séparation.

	Renvoie
	-------
	La différence de distance entre avant et après l'échange des portions de trajets.
	"""
	assert isinstance(trajet1, tuple) and isinstance(trajet2, tuple)

	match [trajet1, trajet2] :
		
		case [[Trajet(), int(ind1)], [Trajet(), int(ind2)]] :
			t1 = trajet1[0]
			t2 = trajet2[0]
			nb1 = t1.nb_clients
			clients1 = t1.clients
			nb2 = t2.nb_clients
			clients2 = t2.clients
			assert 1 <= ind1 < nb1 and 1 <= ind2 < nb2

			cli1 = t1.depot if ind1 == nb1-1 else clients1[ind1+1]
			cli2 = t2.depot if ind2 == nb2-1 else clients2[ind2+1]

			return distance(clients2[ind2], cli1) + distance(clients1[ind1], cli2) - distance(clients2[ind2], cli2) - distance(clients1[ind1], cli1)

		case _ :
			raise AssertionError("trajet1 et trajet2 ne respectent pas le format attendu !")




class Flotte :

	__slots__ = "capacite", "longueur", "nb_trajets", "trajets"

	def __init__(self, capacite :int = 0) :
		self.capacite = capacite
		self.longueur = 0.0
		self.nb_trajets = 0
		self.trajets = []


	def __repr__(self) -> str :
		long = self.longueur
		nb = self.nb_trajets
		return f"Flotte(longueur : {long:.2f}km, contient {nb} camions)"


	def afficher(self, capacite :bool = False) :
		"""
		Affiche la flotte (la longueur et le nombre de camions), et tous les trajets qui la compose.
		Affiche, pour les trajets, la capacité si capacite = True, 
		la liste ordonnée des clients du trajet sinon.

		Paramètres
		----------
		capacite : bool
			Booléen permettant de préciser l'affichage.
		"""
		print(self)
		for t in self.trajets:
			t.afficher(capacite)
		print()



	def ajouter_trajet(self, trajet :Trajet) :
		"""
		Ajoute un itinéraire de livraison.

		Paramètres
		----------
		trajet : Trajet
			Itinéraire de livraison à ajouter.
		"""
		assert isinstance(trajet, Trajet) and trajet.marchandise <= self.capacite

		self.trajets.append(trajet)
		self.longueur += trajet.longueur
		self.nb_trajets += 1



	def retirer_trajet(self, indice :int) -> Trajet :
		"""
		Retire et renvoie un itinéraire de livraison.

		Paramètres
		----------
		indice : int
			Indice de l'itinéraire dans la liste 'trajets'.

		Renvoie
		-------
		L'itinéraire de livraison qui a été retiré.
		"""
		assert isinstance(indice, int) and 0 <= indice < self.nb_trajets

		t = self.trajets.pop(indice)
		self.longueur -= t.longueur
		self.nb_trajets -= 1
		return t
