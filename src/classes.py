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



	def ajouter_client(self, indice :int, client :Client, maj_horaire :bool|None = False) :
		"""
		Ajoute un client à la feuille de route, à la position 'indice'.

		Paramètres
		----------
		indice : int
			Indice où insérer le client.
		client : Client
			Client à ajouter dans l'itinéraire de livraison.
		maj_horaire : bool|None
			True pour mettre à jour toutes les horaires, False sinon.
			None pour ne pas mettre à jour les horaires
		"""
		assert isinstance(client, Client) and (maj_horaire is None or isinstance(maj_horaire, bool))
		assert isinstance(indice, int) and 0 <= indice

		self.longueur += self.dist_ajouter_client(indice, client)
		self.marchandise += client.demande
		self.clients.insert(indice, client)
		self.nb_clients += 1
		if maj_horaire is not None:
			if maj_horaire: indice = 0
			assert self.maj_horaires(indice)



	def retirer_client(self, indice :int, maj_horaire :bool|None = False) -> Client :
		"""
		Retire un client de l'itinéraire.

		Paramètres
		----------
		indice : int
			Indice du client dans la liste non vide 'clients'.
		maj_horaire : bool|None
			True pour mettre à jour toutes les horaires, False sinon.
			None pour ne pas mettre à jour les horaires

		Renvoie
		-------
		Le client se trouvant à l'indice passé en paramètre.
		"""
		assert isinstance(indice, int) and 0 <= indice < self.nb_clients and (maj_horaire is None or isinstance(maj_horaire, bool))

		self.longueur += self.dist_retirer_client(indice)
		cli = self.clients.pop(indice)
		self.nb_clients -= 1
		self.marchandise -= cli.demande
		if maj_horaire is not None:
			if maj_horaire: indice = 0
			if indice == self.nb_clients: assert isinstance(self.horaires.pop(indice), int)
			else: assert self.maj_horaires(indice)
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

		assert self.maj_horaires(ind_debut)
			


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



	def ajouter_tab_client(self, tab_clients :list[Client], maj_horaire :bool|None = False) :
		"""
		Ajoute une liste de clients au début de la feuille de route.

		Paramètres
		----------
		tab_clients : list[Client]
			Liste ordonnée des clients à ajouter dans l'itinéraire de livraison.
		maj_horaire : bool|None
			True pour mettre à jour toutes les horaires, False sinon.
			None pour ne pas mettre à jour les horaires
		"""
		assert isinstance(tab_clients, list) and (maj_horaire is None or isinstance(maj_horaire, bool))

		for client in tab_clients[:0:-1] :
			assert isinstance(client, Client)
			self.ajouter_client(0, client, None)
		self.ajouter_client(0, tab_clients[0], maj_horaire)



	def retirer_tab_client(self, indice :int, maj_horaire :bool|None = False) -> list[Client] :
		"""
		Retire une liste de clients consécutifs de l'itinéraire.

		Paramètres
		----------
		indice : int
			Indice du dernier client.
		maj_horaire : bool|None
			True pour mettre à jour toutes les horaires, False sinon.
			None pour ne pas mettre à jour les horaires

		Renvoie
		-------
		La liste ordonnée des clients retirés du trajet.
		"""
		assert isinstance(indice, int) and (maj_horaire is None or isinstance(maj_horaire, bool))
		assert 1 <= indice < self.nb_clients

		liste_clients = []
		for _ in range(indice) :
			liste_clients.append(self.retirer_client(0, None))
		liste_clients.append(self.retirer_client(0, maj_horaire))
		
		return liste_clients



	def maj_horaires(self, indice :int = 0, client :Client|None = None, modifie :bool = True, liste_clients :list[Client]|None = None, horaires :list[int]|None = None) -> bool :
		"""
		Ajoute 'client' dans la liste des horaires de livraison, ou en retire un à la position 'indice'.

		Paramètres
		----------
		indice : int
			Indice où ajouter le client.
		client : Client|None
			Pour tester l'ajout d'un client (force modifie à False).
		modifie : bool
			True pour effectuer les modifications, False sinon.
		liste_clients : list[Client]|None
			Liste des clients en ajouter si connue, None sinon.
		horaires : list[int]|None
			Liste des horaires si connue, None sinon.

		Renvoie
		-------
		True si la modification peut être effectuée, False sinon.
		"""
		assert isinstance(indice, int) and 0 <= indice and isinstance(modifie, bool)
		if client is not None:
			assert isinstance(client, Client)
			modifie = False

		clients = [] if client is None else [client]
		
		new_horaires = self.horaires[:indice]
		clients += self.clients[indice:]
		
		if liste_clients is not None : 
			assert isinstance(liste_clients, list)
			clients = []
			for cli in liste_clients:
				assert isinstance(cli, Client)
				clients.append(cli)
		if horaires is not None : 
			assert isinstance(horaires, list)
			new_horaires = []
			for horaire in horaires:
				assert isinstance(horaire, int)
				new_horaires.append(horaire)

		for cli in clients:
			precedent = new_horaires[-1] if len(new_horaires) > 0 else self.depot.intervalle_livraison[0]
			if precedent > cli.intervalle_livraison[1]: return False
			new_horaires.append(max(precedent, cli.intervalle_livraison[0]) + cli.temps_livraison)
		
		if modifie: self.horaires = new_horaires.copy()
		
		return new_horaires[-1] <= self.depot.intervalle_livraison[1]



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


	def afficher(self, affichage :bool = False) :
		"""
		Affiche la flotte (la longueur et le nombre de camions), et tous les trajets qui la compose.
		Affiche, pour les trajets, les horaires de livraison si affichage = True,  
		la liste ordonnée des clients du trajet sinon.

		Paramètres
		----------
		affichage : bool
			Booléen permettant de préciser l'affichage.
		"""
		print(self)
		for t in self.trajets:
			t.afficher(affichage)
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
