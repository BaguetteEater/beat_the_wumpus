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
def parcours_largeur_simple (size:int) -> Tuple :

	liste_etat = [[0,0]]

	for etat in liste_etat :
		
		succs = successeurs([etat[0], etat[1]], size)
		for s in succs :
			
			if s not in liste_etat :
				liste_etat.append(s)

	return liste_etat

#def parcours_largeur_memoire (size:int) -> Tuple :
	#chemin = {}



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
		largeur_sans_memoire = parcours_largeur_simple(size)
		#print(largeur_sans_memoire)

		status, msg, gold = wwr.maze_completed()
		print(f"Ca coute {gold}")

		print("press enter for the next maze !!")
		input()
		status, msg, size = wwr.next_maze()


