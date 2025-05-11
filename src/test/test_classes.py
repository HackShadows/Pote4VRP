import unittest
from unittest.mock import NonCallableMock

from classes import *





class TestClassClient(unittest.TestCase) :

	def setUp(self) :
		#Setup
		self.client = Client("id0", (4, 1000), (98, 123456), 330, 10)



	def test_initialisation(self) :
		# Test
		self.assertEqual     (self.client.id                  , "id0"       )
		self.assertTupleEqual(self.client.pos                 , (4 ,   1000))
		self.assertTupleEqual(self.client.intervalle_livraison, (98, 123456))
		self.assertEqual     (self.client.demande             , 330         )
		self.assertEqual     (self.client.temps_livraison     , 10          )



	def test_repr(self) :
		# Test
		self.assertIsInstance(repr(self.client), str)
	


	def test_distance(self) :
		#Setup
		client1 = NonCallableMock(Client); client1.pos = ( 57,-96)
		client2 = NonCallableMock(Client); client2.pos = ( 32, 46)
		client3 = NonCallableMock(Client); client3.pos = (-16, 62)
		# Test
		self.assertAlmostEqual(distance(client1, client2), 144.18391033)
		self.assertAlmostEqual(distance(client1, client3), 174.04884371)
		self.assertAlmostEqual(distance(client2, client3),  50.59644256)





class TestTrajet(unittest.TestCase) :

	def setUp(self) :
		# Setup
		self.depot = NonCallableMock(Client)
		self.depot.pos = (-1, -1)
		self.trajet = Trajet(self.depot)



	def test_init(self) :
		# Test
		self.assertEqual    (self.trajet.longueur   , 0.0       )
		self.assertEqual    (self.trajet.nb_clients , 0         )
		self.assertListEqual(self.trajet.clients    , []        )
		self.assertIs       (self.trajet.depot      , self.depot)
		self.assertEqual    (self.trajet.marchandise, 0         )



	def test_repr(self) :
		# Test
		self.assertIsInstance(repr(self.trajet), str)



	def test_dist_ajouter_client(self) :
		# Setup
		client1 = NonCallableMock(Client); client1.pos = (3  ,  0.5)
		client2 = NonCallableMock(Client); client2.pos = (0  ,  0  )
		client3 = NonCallableMock(Client); client3.pos = (1.7,-10  )

		# Test
		self.assertAlmostEqual(self.trajet.dist_ajouter_client(0, client1), 8.54400374)
		self.trajet.clients.append(client1); self.trajet.nb_clients += 1

		self.assertAlmostEqual(self.trajet.dist_ajouter_client(1, client2), 0.18359295)
		self.trajet.clients.append(client2); self.trajet.nb_clients += 1

		self.assertAlmostEqual(self.trajet.dist_ajouter_client(1, client3), 17.68225967)


	def test_dist_retirer_client(self) :
		# Setup
		client1 = NonCallableMock(Client); client1.pos = (3  ,  0.5)
		client2 = NonCallableMock(Client); client2.pos = (0  ,  0  )
		client3 = NonCallableMock(Client); client3.pos = (1.7,-10  )

		self.trajet.clients.extend([client1, client2, client3])
		self.trajet.nb_clients = 3

		# Test
		self.assertAlmostEqual(self.trajet.dist_retirer_client(1), -2.60468194)
		self.assertAlmostEqual(self.trajet.dist_retirer_client(0), -5.89916957)
		self.assertAlmostEqual(self.trajet.dist_retirer_client(2), -18.1255331)



	def test_dist_remplacer_client(self) :
		# Setup
		client1 = NonCallableMock(Client); client1.pos = ( 3  ,  0.5)
		client2 = NonCallableMock(Client); client2.pos = ( 0  ,  0  )
		client3 = NonCallableMock(Client); client3.pos = ( 1.7,-10  )
		nouveau = NonCallableMock(Client); nouveau.pos = (-2  ,-2   )

		self.trajet.clients.extend([client1, client2, client3])
		self.trajet.nb_clients = 3

		# Test
		self.assertAlmostEqual(self.trajet.dist_remplacer_client(1, nouveau),   1.21951097)
		self.assertAlmostEqual(self.trajet.dist_remplacer_client(0, nouveau), - 3.07074245)
		self.assertAlmostEqual(self.trajet.dist_remplacer_client(2, nouveau), -15.29710597)



	def test_ajouter_client(self) :
		# Setup
		client1 = NonCallableMock(Client)
		client1.pos = (1, 1); client1.demande = 10; client1.intervalle_livraison = (45, 58); client1.temps_livraison = 26
		# Test
		self.trajet.ajouter_client(0, client1)

		self.assertEqual      (self.trajet.nb_clients , 1         )
		self.assertEqual      (self.trajet.clients[0] , client1   )
		self.assertAlmostEqual(self.trajet.longueur   , 5.65685424)
		self.assertEqual      (self.trajet.marchandise, 10        )

		# Setup
		client2 = NonCallableMock(Client)
		client2.pos = (2, 1); client2.demande = 5; client2.intervalle_livraison = (24, 461); client2.temps_livraison = 1
		# Test
		self.trajet.ajouter_client(1, client2)

		self.assertEqual      (self.trajet.nb_clients , 2         )
		self.assertIs         (self.trajet.clients[0] , client1   )
		self.assertIs         (self.trajet.clients[1] , client2   )
		self.assertAlmostEqual(self.trajet.longueur   , 7.43397840)
		self.assertEqual      (self.trajet.marchandise, 15        )



	def test_retirer_client(self) :
		# Setup
		client1 = NonCallableMock(Client)
		client2 = NonCallableMock(Client)
		client1.pos     = (1, 2); client2.pos     = (3, 1)
		client1.demande = 10    ; client2.demande = 5
		client1.intervalle_livraison = (8, 9)
		client2.intervalle_livraison = (10, 100)
		client1.temps_livraison = 21; client2.temps_livraison = 22

		self.trajet.ajouter_client(0, client1)
		self.trajet.ajouter_client(1, client2)

		self.assertEqual      (self.trajet.nb_clients , 2         )
		self.assertAlmostEqual(self.trajet.longueur   ,10.31375520)
		self.assertEqual      (self.trajet.marchandise,15         )

		# Test
		self.assertIs         (self.trajet.retirer_client(1), client2   )
		self.assertEqual      (self.trajet.nb_clients       , 1         )
		self.assertAlmostEqual(self.trajet.longueur         , 7.21110255)
		self.assertEqual      (self.trajet.marchandise      ,10         )

		self.assertIs         (self.trajet.retirer_client(0), client1)
		self.assertEqual      (self.trajet.nb_clients       , 0      )
		self.assertAlmostEqual(self.trajet.longueur         , 0.     )
		self.assertEqual      (self.trajet.marchandise      , 0      )





class TestFlotte(unittest.TestCase) :

	def setUp(self) :
		# Setup
		self.flotte = Flotte(1234)
	


	def test_init(self) :
		# Test
		self.assertEqual    (self.flotte.capacite  , 1234)
		self.assertEqual    (self.flotte.longueur  , 0.0 )
		self.assertEqual    (self.flotte.nb_trajets, 0   )
		self.assertListEqual(self.flotte.trajets   , []  )
	


	def test_repr(self) :
		# Test
		self.assertIsInstance(repr(self.flotte), str)
	


	def test_ajouter_trajet(self) :
		# Setup
		trajet1 = NonCallableMock(Trajet); trajet1.longueur = 34.8; trajet1.marchandise = 1
		# Test
		self.flotte.ajouter_trajet(trajet1)

		self.assertEqual      (self.flotte.capacite  , 1234   )
		self.assertAlmostEqual(self.flotte.longueur  , 34.8   )
		self.assertEqual      (self.flotte.nb_trajets, 1      )
		self.assertIs         (self.flotte.trajets[0], trajet1)

		# Setup
		trajet2 = NonCallableMock(Trajet); trajet2.longueur = 2.00001; trajet2.marchandise = 1
		# Test
		self.flotte.ajouter_trajet(trajet2)

		self.assertEqual      (self.flotte.capacite  , 1234    )
		self.assertAlmostEqual(self.flotte.longueur  , 36.80001)
		self.assertEqual      (self.flotte.nb_trajets, 2       )
		self.assertIs         (self.flotte.trajets[0], trajet1 )
		self.assertIs         (self.flotte.trajets[1], trajet2 )
	


	def test_retire_trajet(self) :
		# Setup
		trajet1 = NonCallableMock(Trajet); trajet1.longueur = 34.8   ; trajet1.marchandise = 1
		trajet2 = NonCallableMock(Trajet); trajet2.longueur = 2.00001; trajet2.marchandise = 1
		self.flotte.ajouter_trajet(trajet1)
		self.flotte.ajouter_trajet(trajet2)

		self.assertEqual      (self.flotte.capacite  , 1234    )
		self.assertAlmostEqual(self.flotte.longueur  , 36.80001)
		self.assertEqual      (self.flotte.nb_trajets, 2       )

		# Test
		self.assertIs         (self.flotte.retirer_trajet(1), trajet2)
		self.assertEqual      (self.flotte.capacite         , 1234   )
		self.assertAlmostEqual(self.flotte.longueur         , 34.8   )
		self.assertEqual      (self.flotte.nb_trajets       , 1      )

		self.assertIs         (self.flotte.retirer_trajet(0), trajet1)
		self.assertEqual      (self.flotte.capacite         , 1234   )
		self.assertAlmostEqual(self.flotte.longueur         , 0      )
		self.assertEqual      (self.flotte.nb_trajets       , 0      )





if __name__ == '__main__':
	unittest.main()
