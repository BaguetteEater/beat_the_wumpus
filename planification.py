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

def successeurs (position:[int, int], size:int) -> Tuple :
	i = position[0]
	j = position[1]

	pos = [
		[i+1, j],
		[i-1, j],
		[i, j+1],
		[i, j-1]
	]

	res = []
	for case in pos :

		if (case[0] > -1 and case[0] < size) and (case[1] > -1 and case[1] < size) and estLibre(case[0], case[1]) :
			res.append(case)

	return res

# Soit une grille de size x size, on va devoir parcourir size² etats
def parcours_largeur_simple (size:int) -> List :

	liste_etats = [[0,0]]

	for etat in liste_etats :

		succs = successeurs(etat, size)
		for s in succs :
			if s not in liste_etats :
				liste_etats.append(s)

	return liste_etats

def parcours_largeur_memoire (size:int, init:Tuple[int, int], but:Tuple[int, int]) -> List :
	
	predecesseurs = {}
	liste_etats = [init]

	for etat in liste_etats :
		
		if etat == but : # On a trouvé notre but, on s'arrete
			break

		succs = successeurs(etat, size)
		for s in succs :
			if s not in liste_etats :
				predecesseurs[tuple(s)] = tuple(etat)
				liste_etats.append(s)
	
	## Init de la boucle
	step = tuple(but) # On cast le but en tuple, car le dictionnaire n'accepte que ça en guise de clef (pas le droit aux listes)
	chemin = [step] # On ajoute le but en tete de liste de notre chemin
	pred = predecesseurs.get(step, -1) # le deuxieme argument est le retour si il n'y a pas de valeur attachée a la clef

	while pred != -1 : 
		chemin.append(pred)
		step = pred
		pred = predecesseurs.get(step, -1)

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
		liste_etat_largeur = parcours_largeur_simple(size)
		chemin = parcours_largeur_memoire(size, [0, 0], [size-1, size-1])

		print(chemin)

		status, msg, gold = wwr.maze_completed()
		print(f"Ca coute {gold}")

		print("press enter for the next maze !!")
		input()
		status, msg, size = wwr.next_maze()


