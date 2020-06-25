import sys
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


# algo glouton sur la largeur d'abord
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
	groupe_id = "Binôme de projet 45"  # votre vrai numéro de groupe
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
		carte = cartographier(wwr, size)

		for row in carte :
			print(row)

		status, msg = wwr.end_map()
		print(status, msg)

		#############
		## Phase 2 ##
		#############
		agent_pos = wwr.get_status()[1]

		liste_etat_largeur = parcours_largeur(size)
		liste_etat_profondeur = parcours_profondeur(size)
		#print(f"parcours largeur : {liste_etat_largeur} \nparcours profondeur : {liste_etat_profondeur}")
		chemin_l = chemin_largeur(size, agent_pos, [size-1, size-1])
		chemin_p = chemin_profondeur(size, agent_pos, [size-1, size-1])
		#chemin_glouton = glouton(size, agent_pos, [size-1, size-1])

		#print(chemin_l)
		#print(chemin_p)
		#print(chemin_glouton)

		status, msg, gold = wwr.maze_completed()
		print(f"Ca coute {gold}")

		print("press enter for the next maze !!")
		input()
		status, msg, size = wwr.next_maze()
