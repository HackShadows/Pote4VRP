import matplotlib.pyplot as plt
import numpy as np
import json




def significants(value :float, n :int) -> float :
	return value
	if value >= 1 :
		first = 0
		v = int(value)
		while v // 10 :
			v //= 10
			first += 1
		return value - (value % 10**(first - n))
	else :
		first = 0
		v = value
		while not(int(v)) :
			v *= 10
			first += 1
		return round(value, first + n - 1)





def gen_dir(mesure :int, situation :int) -> str :
	mesure = ["", "_cap", "_cap_temps"][mesure]
	situation = [1, 2, 3, 4][situation]
	return f"résultats_{situation}{mesure}"



def valeurs_tableaux() :
	for mesure in range(3) :
		for situation in range(4) :
			nom = gen_dir(mesure, situation)
			with open(f"{nom}/RESULT.json", "r") as file :
				data = json.load(file)
			gain       = [significants(100*(1 - ligne["final"     ]/ligne["initial"]), 4) for n_clients, ligne in data.items()]
			itérations = [significants(         ligne["iterations"]/int(n_clients)   , 4) for n_clients, ligne in data.items()]
			temps      = [significants(         ligne["temps"     ]                  , 4) for n_clients, ligne in data.items()]
			temps_w    = [significants(         ligne["temps"     ]/int(n_clients)**2, 4) for n_clients, ligne in data.items()]

			print(f"{nom:<20} : {sum(gain)/len(gain):<20}, {sum(itérations)/len(itérations):<20}, {sum(temps)/len(temps):<20}, {sum(temps_w)/len(temps_w):<20}")



def plot_graph() :
	nb_clients = list()
	gain       = list()
	itérations = list()
	temps      = list()
	for mesure in [0, 1, 2] :
		for situation in [0, 1, 2, 3] :
			nom = gen_dir(mesure, situation)
			with open(f"{nom}/RESULT.json", "r") as file :
				data = json.load(file)

			nb_clients.append(list(map(int, data.keys())))
			gain      .append([100*(1 - ligne["final"]/ligne["initial"]) for ligne in data.values()])
			itérations.append([         ligne["iterations"]              for ligne in data.values()])
			temps     .append([         ligne["temps"]                   for ligne in data.values()])
	
	nb_clients = np.array([sum(nb_clients[j][i] for j in range(len(nb_clients)))/len(nb_clients) for i in range(len(nb_clients[0]))])
	gain       = np.array([sum(      gain[j][i] for j in range(len(     gain )))/len(     gain ) for i in range(len(      gain[0]))])
	itérations = np.array([sum(itérations[j][i] for j in range(len(itérations)))/len(itérations) for i in range(len(itérations[0]))])
	temps      = np.array([sum(     temps[j][i] for j in range(len(     temps)))/len(     temps) for i in range(len(     temps[0]))])

	assert len(nb_clients) == len(gain) == len(itérations) == len(temps)

	fig, ax1 = plt.subplots()

	# Plot percentage
	a, b = np.polyfit(nb_clients, gain, 1)
	ax1.scatter(nb_clients, gain, c='g', label='Percentage (%)', marker='o')
	#ax1.plot(nb_clients, a*nb_clients+b, 'g', linestyle='--')
	ax1.set_xlabel('Nombre de clients')
	ax1.set_ylabel('Gain (%)', color='g')
	ax1.tick_params(axis='y', labelcolor='g')
	ax1.set_ylim(0, 100)

	# Create a second y-axis for quantity
	a, b = np.polyfit(nb_clients, itérations, 1)
	linex = np.array([nb_clients[0], nb_clients[-1]])
	liney = a*linex+b

	ax2 = ax1.twinx()
	ax2.scatter(nb_clients, itérations, c='b', label='Quantity', marker='s')
	ax2.plot(linex, liney, 'b', linestyle='-')
	ax2.set_ylabel("Nombre d'itérations", color='b')
	ax2.tick_params(axis='y', labelcolor='b')

	# Create a third y-axis for time
	ax3 = ax1.twinx()
	ax3.spines['right'].set_position(('outward', 60))  # Offset the third y-axis
	#a, b, c, d = np.polyfit(nb_clients, temps, 3)
	ax3.scatter(nb_clients, temps, c='r', label='Time', marker='^')
	#ax1.plot(nb_clients, a*nb_clients**3+b*nb_clients**2+c*nb_clients+d, 'r', linestyle=':')
	ax3.set_ylabel('Temps', color='r')
	ax3.tick_params(axis='y', labelcolor='r')

	# Add a title and legend
	plt.title("Gain, nombre d'itérations, et temps par clients")
	fig.tight_layout()  # Adjust layout to prevent overlap
	plt.savefig("plot.svg")
	plt.close(fig)



def temps() :
	nb_clients = list()
	itérations = list()
	temps      = list()
	for mesure in [0, 1, 2] :
		for situation in [0, 1, 2, 3] :
			nom = gen_dir(mesure, situation)
			with open(f"{nom}/RESULT.json", "r") as file :
				data = json.load(file)

			nb_clients.append(list(map(int, data.keys())))
			itérations.append([ligne["iterations"] for ligne in data.values()])
			temps     .append([ligne["temps"]      for ligne in data.values()])



	moy_nb_clients = np.array([sum(nb_clients[j][i] for j in range(len(nb_clients)))/len(nb_clients) for i in range(len(nb_clients[0]))])
	moy_itérations = np.array([sum(itérations[j][i] for j in range(len(itérations)))/len(itérations) for i in range(len(itérations[0]))])
	moy_temps      = np.array([sum(     temps[j][i] for j in range(len(     temps)))/len(     temps) for i in range(len(     temps[0]))])

	calc1 = moy_nb_clients**2 * moy_itérations / moy_temps


	moy_c_it = np.array([sum(nb_clients[j][i]**2 * itérations[j][i] for j in range(len(nb_clients)))/len(nb_clients) for i in range(len(nb_clients[0]))])
	calc2 = moy_c_it / moy_temps


	calc3 = np.array([sum(nb_clients[j][i]**2 * itérations[j][i] / temps[j][i] for j in range(len(nb_clients)))/len(nb_clients) for i in range(len(nb_clients[0]))])

	assert len(nb_clients[0]) == len(calc1) == len(calc2) == len(calc3)

	fig, ax1 = plt.subplots()

	# Plot percentage
	#a, b = np.polyfit(nb_clients, gain, 1)
	ax1.scatter(nb_clients[0], calc1, c='g', label='Percentage (%)', marker='o')
	#ax1.plot(nb_clients, a*nb_clients+b, 'g', linestyle='--')
	ax1.set_xlabel('Nombre de clients')
	ax1.set_ylabel('Calc1', color='g')
	ax1.tick_params(axis='y', labelcolor='g')

	# Create a second y-axis for quantity
	#a, b = np.polyfit(nb_clients, itérations, 1)
	#linex = np.array([nb_clients[0], nb_clients[-1]])
	#liney = a*linex+b

	ax2 = ax1.twinx()
	ax2.scatter(nb_clients[0], calc2, c='b', label='Quantity', marker='s')
	#ax2.plot(linex, liney, 'b', linestyle='-')
	ax2.set_ylabel("Calc2", color='b')
	ax2.tick_params(axis='y', labelcolor='b')

	# Create a third y-axis for time
	ax3 = ax1.twinx()
	ax3.spines['right'].set_position(('outward', 60))  # Offset the third y-axis
	#a, b, c, d = np.polyfit(nb_clients, temps, 3)
	ax3.scatter(nb_clients[0], calc3, c='r', label='Time', marker='^')
	#ax1.plot(nb_clients, a*nb_clients**3+b*nb_clients**2+c*nb_clients+d, 'r', linestyle=':')
	ax3.set_ylabel('Calc3', color='r')
	ax3.tick_params(axis='y', labelcolor='r')

	# Add a title and legend
	plt.title("Gain, nombre d'itérations, et temps par clients")
	fig.tight_layout()  # Adjust layout to prevent overlap
	plt.show()
	#plt.savefig("plot.svg")
	#plt.close(fig)



if __name__ == '__main__' :
	temps()
