import sys
from queue import PriorityQueue
from typing import Dict, Tuple, List, Union
from wumpus_cli.lib.wumpus_client import WumpusWorldRemote
from cartographie import cartographier

carte = []
contenu_interdit = ['W', 'P']

def estLibre(i:int, j:int) -> bool :
	for element in contenu_interdit :
		for contenu in carte[i][j] :
			if contenu == element :
				return False

	return True

def successeurs (position:Tuple[int, int], size:int) -> Tuple :
	i = position[0]
	j = position[1]

	pos = [
		(i+1, j),
		(i-1, j),
		(i, j+1),
		(i, j-1)
	]

	res = []
	for case in pos :

		if (case[0] > -1 and case[0] < size) and (case[1] > -1 and case[1] < size) and estLibre(case[0], case[1]) :
			res.append(case)

	return res

# Soit une grille de size x size, on va devoir parcourir size² etats
def parcours_largeur (size:int) -> List :

	liste_etats = [(0,0)]

	for etat in liste_etats :

		succs = successeurs(etat, size)
		for s in succs :
			if s not in liste_etats :
				liste_etats.append(s)

	return liste_etats

def parcours_profondeur (size:int) -> List :

	liste_etats = [(0,0)]

	for etat in liste_etats :

		succs = successeurs(etat, size)
		offset = 1
		for s in succs :
			if s not in liste_etats :
				# soit [0, 1, 2] et s de 1 = [4, 5]. On doit inserer 4 en 1 + 1 = 2 et 5 en 1 + 2 = 3
				# offset est initialisé a 1 et a chaque insertion est augmenté de un
				idx = liste_etats.index(etat) + offset
				liste_etats.insert(idx, tuple(s))
				offset += 1

	return liste_etats

def chemin_largeur (size:int, init:Tuple[int, int], but:Tuple[int, int]) -> Tuple :
	
	predecesseurs = {}
	liste_etats = [init]

	for etat in liste_etats :
		
		if etat == but : # On a trouvé notre but, on s'arrete
			break

		succs = successeurs(etat, size)
		for s in succs :
			if s not in liste_etats :
				predecesseurs[tuple(s)] = tuple(etat)
				liste_etats.append(tuple(s))

	return get_chemin_predecesseurs(predecesseurs, but)

def chemin_profondeur (size:int, init:Tuple[int, int], but:Tuple[int, int]) -> List :
	
	predecesseurs = {}
	liste_etats = [init]

	for etat in liste_etats :
		
		if etat == but : # On a trouvé notre but, on s'arrete
			break

		succs = successeurs(etat, size)
		offset = 1
		for s in succs :
			if s not in liste_etats :
				
				predecesseurs[tuple(s)] = tuple(etat)
				# soit [0, 1, 2] et s de 1 = [4, 5]. On doit inserer 4 en 1 + 1 = 2 et 5 en 1 + 2 = 3
				# offset est initialisé a 1 et a chaque insertion est augmenté de un
				idx = liste_etats.index(etat) + offset
				liste_etats.insert(idx, tuple(s))
				offset += 1

	return get_chemin_predecesseurs(predecesseurs, but)

def get_chemin_predecesseurs (predecesseurs:Dict, but:Tuple[int, int]) :

	## Init de la boucle
	step = tuple(but) # On cast le but en tuple, car le dictionnaire n'accepte que ça en guise de clef (pas le droit aux listes)
	chemin = [step] # On ajoute le but en tete de liste de notre chemin
	pred = predecesseurs.get(step, -1) # le deuxieme argument est le retour si il n'y a pas de valeur attachée a la clef

	while pred != -1 : 
		chemin.append(pred)
		step = pred
		pred = predecesseurs.get(step, -1)

	chemin.reverse()
	chemin.pop(0) # le premier element etant la position de depart, cela ne nous interesse pas
	return chemin


# Pour notre heuristique, nous choissons la distance de Manhattan entre notre position et l'etat but
# En effet, nous travaillons sur une grille de taille size x size
# or la distance de Manhattan - dont la formule est : |x0−x1|+|y0−y1| -
# est faite pour calculer la distance entre x et y dans un quadrillage.
def distance_manhattan(depart:Tuple[int, int], but:Tuple[int, int]) -> int : 
	xdiff = abs(depart[0] - but[0])
	ydiff = abs(depart[1] - but[1])

	return xdiff + ydiff

# Retourne les successeurs qui ne sont pas des culs-de-sac
def successeurs_glouton (position:Tuple[int, int], size:int, dead_end:Dict, chemin:Tuple) -> Tuple :
	succs = successeurs(position, size)
	res = []

	for s in succs :
		if dead_end[s] == False and s not in chemin:
			res.append(s)

	return res

def get_minimum_distance_state (successeurs:Tuple, but:Tuple) :

	distance = {} # liste des distance en fonction des etats
	for s in successeurs :
		distance[s] = distance_manhattan(s, but) # On calcule la distance de manhattan entre un candidat et le but

	# Minimum se presente sous la forme ((i, j), distance)
	minimum = distance.popitem()
	for item in distance.items() :
		if item[1] < minimum[1] :
			minimum = item

	return minimum

# Parcourt en largeur les etats jusqu'a tomber sur notre but
# A chaque iteration, on calcule le cout pour aller de l'etat initial vers la l'etat cible à partir de l'etat courant
# Si jamais un chemin avait deja été trouvé vers la cible, on prend le chemin le moins couteux
# On utilise une distance de manhattan ainsi qu'un cout cumulé depuis l'etat initial tel que :
# g = f + h avec g le cout total, f le cout depuis l'etat inital et h notre heuristique
def a_etoile (size:int, init:Tuple, but:Tuple) :
	queue = PriorityQueue() # une
	queue.put(init, 0)

	predecesseurs = {}
	liste_couts = {} # Dico des couts en fonctions des etats

	predecesseurs[init] = None
	liste_couts[init] = 0 

	# le prix pour aller d'une case à une autre
	# il est le meme pour toutes les cases
	cout_gold = 10
	
	while not queue.empty(): # Tant que la queue n'est pas vide
		etat = queue.get() # On recupere un etat

		if etat == but : # on arrete dès qu'on a trouvé notre but
			break
		
		for s in successeurs(etat, size):

			# On calcule le nouveau cout pour aller en s
			# Si mon successeur n'est pas encore incrit dans la liste OU BIEN, son nouveau cout est plus interessant -> je visite
			cout_depuis_init = liste_couts[etat] + cout_gold
			if s not in liste_couts or cout_depuis_init < liste_couts[s]:
				liste_couts[s] = cout_depuis_init
				g = cout_depuis_init + distance_manhattan(but, s) # le calcul g = f + h est ici
				queue.put(s, g)
				predecesseurs[s] = etat
	
	return get_chemin_predecesseurs(predecesseurs, but)


def get_gold_position (size:int) :

	liste_pos_gold = []
	for i in range(size) :
		for j in range(size) :
			if 'G' in carte[i][j] :
				liste_pos_gold.append((i, j))

	return liste_pos_gold

# algo glouton
# Dans cette version, on recommence a calculer un chemin si jamais nous tombons sur un cul-de-sac
# C'est TRES gourmand et ça ne garantis pas le meilleur chemin
# Mais si il existe un chemin, il le trouvera
def glouton (size:int, init:Tuple[int, int], but:Tuple[int, int]) -> List :

	chemin = [init] # La où se place notre agent
	dead_end = {}

	# Si un etat == True alors cet etat est un cul-de-sac
	for i in range(size) :
		for j in range(size) :
			dead_end[(i, j)] = False 

	while dead_end.get(init) == False and chemin[len(chemin)-1] != tuple(but): # tant que ma case de depart n'est pas un cul de sac alors je cherche un autre chemin et que je n'ai pas atteint le but
		
		for etat in chemin :

			if etat == tuple(but) :
				break

			succs = successeurs_glouton(etat, size, dead_end, chemin)
			if len(succs) != 0 : # si je peux continuer a construire un chemin
				minimum = get_minimum_distance_state(succs, but)
				chemin.append(minimum[0])
			else :
				dead_end[etat] = True # si il n'y a pas de successeurs alors je suis dans un cul-de-sac
				chemin = [init]
				break

	return chemin

if __name__ == "__main__":

	server = "http://localhost:8080"
	groupe_id = "PRJ45"  # votre vrai numéro de groupe
	names = "Ulysse Brehon et Luis Enrique Gonzalez Hilario"  # vos prénoms et noms

	try:
		wwr = WumpusWorldRemote(server, groupe_id, names)
	except HTTPError as e:
		print(e)
		print("Try to close the server (Ctrl-C in terminal) and restart it")
		sys.exit(-1)

	status, msg, size = wwr.next_maze()
	while status == "[OK]":
		
		#############
		## PHASE 1 ##
		#############
		print("       =====================\n")
		print(f"Carte de {size}*{size}")
		carte = cartographier(wwr, size)

		for row in carte : # On imprime la carte obtenue
			print(row)

		status, msg = wwr.end_map()
		print(status, msg)
		print("\n")

		#############
		## Phase 2 ##
		#############
		agent_pos = wwr.get_position()
		gold_positions = get_gold_position(size)

		print(f"Goals (gold pos) : {gold_positions}")

		for gold_pos in gold_positions :
			
			print(f"Current goal : {gold_pos}")

			chemin = a_etoile(size, agent_pos, gold_pos)
			print(f"A* chemin : {chemin}")
			if len(chemin) != 0 and chemin[-1] == gold_pos : # Si j'ai un chemin et le dernier element de ma liste est bien la case contenant l'or
				for case in chemin :
					wwr.go_to(case[0], case[1])

			agent_pos = wwr.get_position()

		chemin = a_etoile(size, agent_pos, (0,0)) # On a attrapé tout l'or, on peut rentrer
		for case in chemin :
			wwr.go_to(case[0], case[1])

		status, msg, gold = wwr.maze_completed()
		print(f"Total cost : {gold['total_cost']}, total reward : {gold['total_reward']}\n\n")

		status, msg, size = wwr.next_maze()
