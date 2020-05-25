from lib.gopherpysat import Gophersat
from typing import Dict, Tuple, List, Union
from wumpus import WumpusWorld
import itertools

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
# Tested and Working
def insert_wumpus_regle(gs:Gophersat, wumpus_voca:Tuple) :

	wumpus_voca2 = wumpus_voca.copy()
	for case in wumpus_voca :
		wumpus_voca2.remove(case)

		for c in wumpus_voca2 :
			gs.push_pretty_clause([f"-{case}", f"-{c}"])

	gs.push_pretty_clause(wumpus_voca)

# Tested and Working
def insert_safety_regle(gs:Gophersat) :

	gs.push_pretty_clause(["-W00"])
	gs.push_pretty_clause(["-T00"])

# Prend un caractere de la chaine de description d'une case et la position du contenu
# Retourne un Tuple avec les clauses a inserer dans le modèle
def wumpus_to_clause(single_case_content:str, position:Tuple[int, int]) :
	switcher = {
		".":[
				f"-W{position[0]}{position[1]}", 
				f"-T{position[0]}{position[1]}", 
				f"-G{position[0]}{position[1]}", 
				f"-B{position[0]}{position[1]}", 
				f"-S{position[0]}{position[1]}"
			],
		"W":[f"W{position[0]}{position[1]}"],
		"P":[f"T{position[0]}{position[1]}"],
		"S":[f"S{position[0]}{position[1]}"],
		"G":[f"G{position[0]}{position[1]}"],
		"B":[f"B{position[0]}{position[1]}"],
		"-W":[f"-W{position[0]}{position[1]}"],
		"-P":[f"-T{position[0]}{position[1]}"],
		"-S":[f"-S{position[0]}{position[1]}"],
		"-G":[f"-G{position[0]}{position[1]}"],
		"-B":[f"-B{position[0]}{position[1]}"]
	}
	return switcher.get(single_case_content, -1)

def push_clause_from_wumpus(gs:Gophersat, is_positive:bool, case_contents:str, position:Tuple[int, int]):
	for case_content in case_contents :
		if is_positive == False :
			clauses = wumpus_to_clause(f"-{case_content}", position)
		else :
			clauses = wumpus_to_clause(case_content, position)
		
		if clauses == -1 :
			print("Error : Invalid case contents, have you inserted multiple case content at once ?")
		else :
			for clause in clauses : # On doit inserer les clauses une a une
				gs.push_pretty_clause([clause])

def is_case_dangereuse(gs:Gophersat, position:Tuple[int, int]) -> bool :

	push_clause_from_wumpus(gs, False, "W", position) # On teste la contradiction sur la position du Wumpus

	if gs.solve() == False : # Si la non-existence du Wumpus a cet endroit entraine contradiction, alors la case est dangereuse
		gs.pop_clause()
		return True

	gs.pop_clause()
	push_clause_from_wumpus(gs, False ,"P", position) # On teste la contradiction sur la position d'un trou
	
	if gs.solve() == False : # Si la non-existence du Wumpus a cet endroit entraine contradiction, alors la case est dangereuse
		gs.pop_clause()
		return True

	gs.pop_clause()
	return False # sinon la case n'est pas dangeureuse

if __name__ == "__main__":

	taille_grille = 4

	wumpus_voca = generate_wumpus_voca(taille_grille)
	gold_voca = generate_gold_voca(taille_grille)
	stench_voca = generate_stench_voca(taille_grille)
	brise_voca = generate_brise_voca(taille_grille)
	trou_voca = generate_trou_voca(taille_grille)

	voc = wumpus_voca + gold_voca + stench_voca + brise_voca + trou_voca

	gs = Gophersat(gophersat_exec, voc)

	# On modelise les regles
	insert_safety_regle(gs)
	insert_wumpus_regle(gs, wumpus_voca)

	# On crée le monde
	ww = WumpusWorld()
	print(ww)

	# On analyse notre position, qui est (0, 0) pour 0 gold
	# Puis on ajoute le resultat au modèle
	case_contents = ww.get_percepts()[2]
	push_clause_from_wumpus(gs, True, case_contents, ww.get_position())

	for i in range(taille_grille) :
		for j in range(taille_grille) :
			if i != 0 or j != 0 : # On ne regarde pas la premiere case pour economiser l'argent
				
				if is_case_dangereuse(gs, [i, j]) :
					case_contents = ww.cautious_probe(i, j)[1]
					print(i, j, case_contents)
				else :
					case_contents = ww.cautious_probe(i, j)[1]
					print(i, j, case_contents)
				

	for vector in ww.get_knowledge() :
		print(vector)
		
	print(gs.solve())
	print(gs.get_pretty_model())