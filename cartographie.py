from lib.gopherpysat import Gophersat
from typing import Dict, Tuple, List, Union
from wumpus import WumpusWorld
import itertools

gophersat_exec = "./lib/gophersat-1.1.6"


# Retourne une List composée de tous les symboles representant les positions possible du Wumpus
# Ex: [W00, W01, W02, W03, W10, W11, W12, ..., W33] pour une grille 4*4
def generate_wumpus_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"W{i}{j}")

	return res

def generate_stench_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"S{i}{j}")

	return res

def generate_gold_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"G{i}{j}")

	return res

def generate_brise_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"B{i}{j}")

	return res

def generate_trou_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			res.append(f"T{i}{j}")

	return res

def insert_all_regles (gs:Gophersat, wumpus_voca:List, trou_voca:List, brise_voca:List, stench_voca:List) : 

	insert_only_one_wumpus_regle(gs, wumpus_voca)
	insert_safety_regle(gs)
	insert_trou_regle(gs, trou_voca, brise_voca)
	insert_brise_regle(gs, brise_voca, trou_voca)
	insert_wumpus_stench_regle(gs, wumpus_voca, stench_voca)
	insert_stench_regle(gs, wumpus_voca, stench_voca)
	insert_une_menace_par_case_regle(gs, wumpus_voca, trou_voca)

# Il y a forcement un Wumpus et il en existe un seul
# WIJ <-> non(WAB) et non(WAC) et non(WAD) ... 
# Tested and Working
def insert_only_one_wumpus_regle (gs:Gophersat, wumpus_voca:List) :

	wumpus_voca2 = wumpus_voca.copy()
	for case in wumpus_voca :
		wumpus_voca2.remove(case)

		for c in wumpus_voca2 :
			gs.push_pretty_clause([f"-{case}", f"-{c}"])

	gs.push_pretty_clause(wumpus_voca)

# Tested and Working
def insert_safety_regle (gs:Gophersat) :

	gs.push_pretty_clause(["-W00"])
	gs.push_pretty_clause(["-T00"])

# Wij -> -Tij
# Tij -> -Wij
# On ne peut pas avoir de wumpus en (i, j) si il y a un trou en (i, j)
def insert_une_menace_par_case_regle (gs:Gophersat, wumpus_voca:List, trou_voca:List) :

	trou_voca_pile = trou_voca.copy()
	wumpus_voca_pile = wumpus_voca.copy()

	for i in range(len(wumpus_voca)) :

		trou = trou_voca_pile.pop()
		wumpus = wumpus_voca_pile.pop()
		gs.push_pretty_clause([f"-{wumpus}", f"-{trou}"])
		gs.push_pretty_clause([f"-{trou}", f"-{wumpus}"])
		print(wumpus, trou)


# Si il y a un trou en (i, j) Alors il y a une brise en (i-1, j), (i+1, j), (i, j-1) et (i, j+1)
# Tij -> B(i-1)j ET B(i+1)j ET Bi(j-1) ET Bi(j+1)
# Devenant -Tij v B(i-1)j ; -Tij v B(i+1)j ; -Tij v Bi(j-1) ; -Tij v Bi(j+1)
# Tested and working
def insert_trou_regle (gs:Gophersat, trou_voca:List, brise_voca:List) :

	for trou in trou_voca :
		
		# Soit le symbole Tij
		i = int(trou[1]) # On recupere l'index i
		j = int(trou[2]) # On recupere l'index j

		brises = []

		if f"B{i+1}{j}" in brise_voca :
			brises.append(f"B{i+1}{j}")

		if f"B{i-1}{j}" in brise_voca :
			brises.append(f"B{i-1}{j}")

		if f"B{i}{j+1}" in brise_voca :
			brises.append(f"B{i}{j+1}")

		if f"B{i}{j-1}" in brise_voca :
			brises.append(f"B{i}{j-1}")

		for brise in brises :
			gs.push_pretty_clause([f"-{trou}", brise])


# On insere -Bij ou T(i-1)j ou T(i+1)j ou Ti(j-1) ou Ti(j+1)
# Tested and working
def insert_brise_regle (gs:Gophersat, brise_voca:List, trou_voca:List) :
	
	for brise in brise_voca :
		
		# Soit le symbole Bij
		i = int(brise[1]) # On recupere l'index i
		j = int(brise[2]) # On recupere l'index j

		trous = []

		if f"T{i+1}{j}" in trou_voca :
			trous.append(f"T{i+1}{j}")

		if f"T{i-1}{j}" in trou_voca :
			trous.append(f"T{i-1}{j}")

		if f"T{i}{j+1}" in trou_voca :
			trous.append(f"T{i}{j+1}")

		if f"T{i}{j-1}" in trou_voca :
			trous.append(f"T{i}{j-1}")

		clause = trous + [f"-{brise}"]
		gs.push_pretty_clause(clause)


# Si il y a un wumpus en (i, j) Alors il y a une stench en (i-1, j), (i+1, j), (i, j-1) et (i, j+1)
# Wij -> S(i-1)j ET S(i+1)j ET Si(j-1) ET Si(j+1)
# Devenant -Wij v S(i-1)j ; -Wij v S(i+1)j ; -Wij v Si(j-1) ; -Wij v Si(j+1)
# Tested and Working
def insert_wumpus_stench_regle (gs:Gophersat, wumpus_voca:List, stench_voca:List) :

	for wumpus in wumpus_voca :
		
		# Soit le symbole Tij
		i = int(wumpus[1]) # On recupere l'index i
		j = int(wumpus[2]) # On recupere l'index j

		stenches = []

		if f"S{i+1}{j}" in stench_voca :
			stenches.append(f"S{i+1}{j}")

		if f"S{i-1}{j}" in stench_voca :
			stenches.append(f"S{i-1}{j}")

		if f"S{i}{j+1}" in stench_voca :
			stenches.append(f"S{i}{j+1}")

		if f"S{i}{j-1}" in stench_voca :
			stenches.append(f"S{i}{j-1}")

		for stench in stenches :
			gs.push_pretty_clause([f"-{wumpus}", stench])


# On insere a chaque fin de boucle -Sij ou W(i-1)j ou W(i+1)j ou Wi(j-1) ou Wi(j+1)
# Tested and Working
def insert_stench_regle (gs:Gophersat, wumpus_voca:List, stench_voca:List) :
		
	for stench in stench_voca :
		
		# Soit le symbole Wij
		i = int(stench[1]) # On recupere l'index i
		j = int(stench[2]) # On recupere l'index j

		wumpuses = []

		if f"W{i+1}{j}" in wumpus_voca :
			wumpuses.append(f"W{i+1}{j}")

		if f"W{i-1}{j}" in wumpus_voca :
			wumpuses.append(f"W{i-1}{j}")

		if f"W{i}{j+1}" in wumpus_voca :
			wumpuses.append(f"W{i}{j+1}")

		if f"W{i}{j-1}" in wumpus_voca :
			wumpuses.append(f"W{i}{j-1}")

		clause = wumpuses + [f"-{stench}"]
		gs.push_pretty_clause(clause)


# Prend un caractere de la chaine de description d'une case et la position du contenu
# Retourne un Tuple avec les clauses a inserer dans le modèle
def wumpus_to_clause (single_case_content:str, position:Tuple[int, int]) :
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
	}
	return switcher.get(single_case_content, -1)

def push_clause_from_wumpus (gs:Gophersat, case_contents:str, position:Tuple[int, int]):

	facts = []
	for case_content in case_contents :
		
		tmp_facts = wumpus_to_clause(case_content, position)
		
		if tmp_facts == -1 :
			print("Error : Invalid case contents, have you inserted multiple case content at once ?")
			return -1
		else :
			facts = facts + tmp_facts	

	facts = facts + get_implicit_negative_facts(facts, position)	

	for fact in facts : # On doit inserer les clauses une a une
		gs.push_pretty_clause([fact])

# On ajoute les faits perçu de par leur non-presence
# Exemple : On repere Bij, cela veut dire qu'il n'a pas de wumpus, ni de trou, ni de stench etc....
def get_implicit_negative_facts (facts:List, position:Tuple[int, int]) :
	possible_case_content = ["W", "T", "G", "S", "B"]
	need_to_add = True
	facts_to_add = []

	for content in possible_case_content :
		for fact in facts :

			if content in fact :
				need_to_add = False

		if need_to_add :
			facts_to_add.append(f"-{content}{position[0]}{position[1]}")

		need_to_add = True

	return facts_to_add


# True si un wumpus en i, j est possible
# False si un wumpus i, j est impossible
def is_wumpus_possible(gs, position:Tuple[int, int]) -> bool :

	gs.push_pretty_clause([f"W{position[0]}{position[1]}"])

	res = gs.solve()

	gs.pop_clause()

	return res

def is_trou_possible(gs, position:Tuple[int, int]) -> bool :

	gs.push_pretty_clause([f"T{position[0]}{position[1]}"])

	res = gs.solve()

	gs.pop_clause()

	return res

def should_I_be_cautious (gs:Gophersat, position:Tuple[int, int]) -> bool :

	print(f"wumpus possible : {is_wumpus_possible(gs, position)} ----- trou possible : {is_trou_possible(gs, position)}")
	return is_wumpus_possible(gs, position) or is_trou_possible(gs, position)


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
	insert_all_regles(gs, wumpus_voca, trou_voca, brise_voca, stench_voca)
	print(f"Modelisation reussie : {gs.solve()}")

	# On crée le monde
	ww = WumpusWorld()
	print(ww)

	# On analyse notre position, qui est (0, 0) pour 0 gold
	# Puis on ajoute le resultat au modèle
	case_contents = ww.get_percepts()[2]
	push_clause_from_wumpus(gs, case_contents, ww.get_position())
	print(f"{gs.solve()}")
	print(f"{gs.get_pretty_model()}")

	print("==========================\n\n")

	for i in range(4) :
		for j in range(4) :
			if i != 0 or j != 0 : # On ne regarde pas la premiere case pour economiser l'argent
				
				if should_I_be_cautious(gs, [i, j]) :
					case_contents = ww.cautious_probe(i, j)[1]
				else :
					case_contents = ww.probe(i, j)[1]

				push_clause_from_wumpus(gs, case_contents, [i, j])
				print(f"[{i}, {j}] - case_contents : {case_contents}")
				print(f"Satisfiabilité : {gs.solve()}")
				for vector in ww.get_knowledge() :
					print(vector)
				print("\n --- \n")
	

	print("\n\n==========================")
	for vector in ww.get_knowledge() :
		print(vector)

	print(f"Satisfiabilité : {gs.solve()}")
	print(f"Modele trouvé :\n {gs.get_pretty_model()} \n ---")
	print(f"cout en or : {ww.get_cost()}")