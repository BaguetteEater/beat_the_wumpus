from lib.gopherpysat import Gophersat
import itertools
from typing import Dict, Tuple, List, Union

gophersat_exec = "./lib/gophersat-1.1.6"


# Retourne une List composée de tous les symboles representant les positions possible du Wumpus
# Ex: [W00, W01, W02, W03, W10, W11, W12, ..., W33] pour une grille 4*4
def generate_wumpus_voca(taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"W{i}{j}")

	return res

def generate_stench_voca(taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"S{i}{j}")

	return res

def generate_gold_voca(taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"G{i}{j}")

	return res

def generate_brise_voca(taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"B{i}{j}")

	return res

def generate_trou_voca(taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"T{i}{j}")

	return res

# Il y a forcement un Wumpus et il en existe un seul
# WIJ <-> non(WAB) et non(WAC) et non(WAD) ... 
def insert_wumpus_regle(gs, wumpus_voca) :

	wumpus_voca2 = wumpus_voca.copy()
	for case in wumpus_voca :
		wumpus_voca2.remove(case)

		for c in wumpus_voca2 :
			gs.push_pretty_clause([f"-{case}", f"-{c}"])

	gs.push_pretty_clause(wumpus_voca)



if __name__ == "__main__":

	wumpus_voca = generate_wumpus_voca(4)
	gold_voca = generate_gold_voca(4)
	stench_voca = generate_stench_voca(4)
	brise_voca = generate_brise_voca(4)
	trou_voca = generate_trou_voca(4)

	voc = wumpus_voca + gold_voca + stench_voca + brise_voca + trou_voca

	gs = Gophersat(gophersat_exec, voc)

	insert_wumpus_regle(gs, wumpus_voca)

	print(gs.dimacs())
	print(gs.solve())


	#ww = WumpusWorld()
 	#print(ww.get_percepts())
  	#print(ww.go_to(0, 1))
   	#print(ww.get_percepts())
    #print(ww.get_position())
    #print(ww.go_to(0, 2))

    #print(ww)