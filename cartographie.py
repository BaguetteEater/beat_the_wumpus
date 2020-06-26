from lib.gopherpysat import Gophersat
from typing import Dict, Tuple, List, Union
import itertools
import random
import time
import sys
from wumpus_cli.lib.wumpus_client import WumpusWorldRemote

gophersat_exec = "./lib/gophersat-1.1.6"

## On genere le voca avec toujours 4 chiffres pour extraire plus facilement les coordonnées lors de l'insertion des regles

# Retourne une List composée de tous les symboles representant les positions possible du Wumpus
# Ex: [W0000, W0001, W0002, W0003, W0100, W0101, W0102, ..., W0303] pour une grille 4*4
def generate_wumpus_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			if (i < 10 and j < 10) :
				res.append(f"W0{i}0{j}")
			elif (i < 10 and j > 9) :
				res.append(f"W0{i}{j}")
			elif (i > 9 and j < 10) :
				res.append(f"W{i}0{j}")
			else :
				res.append(f"W{i}{j}")

	return res

def generate_stench_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			if (i < 10 and j < 10) :
				res.append(f"S0{i}0{j}")
			elif (i < 10 and j > 9) :
				res.append(f"S0{i}{j}")
			elif (i > 9 and j < 10) :
				res.append(f"S{i}0{j}")
			else :
				res.append(f"S{i}{j}")

	return res

def generate_gold_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			if (i < 10 and j < 10) :
				res.append(f"G0{i}0{j}")
			elif (i < 10 and j > 9) :
				res.append(f"G0{i}{j}")
			elif (i > 9 and j < 10) :
				res.append(f"G{i}0{j}")
			else :
				res.append(f"G{i}{j}")

	return res

def generate_brise_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			if (i < 10 and j < 10) :
				res.append(f"B0{i}0{j}")
			elif (i < 10 and j > 9) :
				res.append(f"B0{i}{j}")
			elif (i > 9 and j < 10) :
				res.append(f"B{i}0{j}")
			else :
				res.append(f"B{i}{j}")

	return res

def generate_trou_voca (taille_grille: int) :
	res = []
	for i in range(taille_grille):
		for j in range(taille_grille):
			if (i < 10 and j < 10) :
				res.append(f"T0{i}0{j}")
			elif (i < 10 and j > 9) :
				res.append(f"T0{i}{j}")
			elif (i > 9 and j < 10) :
				res.append(f"T{i}0{j}")
			else :
				res.append(f"T{i}{j}")

	return res

## Fin generation voca

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

# Il n'y a ni wumpus, ni trou en (0,0)
# Tested and Working
def insert_safety_regle (gs:Gophersat) :

	gs.push_pretty_clause(["-W0000"])
	gs.push_pretty_clause(["-T0000"])

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


def int_to_two_digits_str (i:int, number_to_apply:int = 0) -> str :
	i = i + number_to_apply

	if(i < 10) :
		return f"0{i}"
	else :
		return f"{i}"

# Si il y a un trou en (i, j) alors il y a une brise en (i-1, j), (i+1, j), (i, j-1) et (i, j+1)
# Tij -> B(i-1)j ET B(i+1)j ET Bi(j-1) ET Bi(j+1)
# Devenant -Tij v B(i-1)j ; -Tij v B(i+1)j ; -Tij v Bi(j-1) ; -Tij v Bi(j+1)
# Tested and working
def insert_trou_regle (gs:Gophersat, trou_voca:List, brise_voca:List) :

	for trou in trou_voca :
		
		# Soit le symbole Tij, une chaine de caractere avec i et j appartient a [0..99]
		# On enleve la lettre et on recupere i et j
		ij = trou[1:]
		i = int(ij[:2]) # On prend les deux premiers chiffres pour l'indice i
		j = int(ij[2:]) # On prend les deux derniers chiffres pour l'indice j

		i_moins_1 = int_to_two_digits_str(i, -1)
		i_plus_1 = int_to_two_digits_str(i, 1)

		j_moins_1 = int_to_two_digits_str(j, -1)
		j_plus_1 = int_to_two_digits_str(j, 1)

		i = int_to_two_digits_str(i)
		j = int_to_two_digits_str(j)

		brises = []

		if f"B{i_plus_1}{j}" in brise_voca :
			brises.append(f"B{i_plus_1}{j}")

		if f"B{i_moins_1}{j}" in brise_voca :
			brises.append(f"B{i_moins_1}{j}")

		if f"B{i}{j_plus_1}" in brise_voca :
			brises.append(f"B{i}{j_plus_1}")

		if f"B{i}{j_moins_1}" in brise_voca :
			brises.append(f"B{i}{j_moins_1}")

		for brise in brises :
			gs.push_pretty_clause([f"-{trou}", brise])


# Bij <-> ( T(i-1)j ou T(i+1)j ou Ti(j-1) ou Ti(j+1) )
# C'est a dire que une brise en (i, j) equivault à au moins un trou autour
# On insere -Bij ou T(i-1)j ou T(i+1)j ou Ti(j-1) ou Ti(j+1) ; -Tij ou B(i-1)j ou B(i+1)j ou Bi(j-1) ou Bi(j+1)
# Tested and working
def insert_brise_regle (gs:Gophersat, brise_voca:List, trou_voca:List) :
	
	#-Bij ou T(i-1)j ou T(i+1)j ou Ti(j-1) ou Ti(j+1)
	for brise in brise_voca :
		
		# Soit le symbole Bij
		# On enleve la lettre et on recupere i et j
		ij = brise[1:]
		i = int(ij[:2]) # On prend les deux premiers chiffres pour l'indice i
		j = int(ij[2:]) # On prend les deux derniers chiffres pour l'indice j

		i_moins_1 = int_to_two_digits_str(i, -1)
		i_plus_1 = int_to_two_digits_str(i, 1)

		j_moins_1 = int_to_two_digits_str(j, -1)
		j_plus_1 = int_to_two_digits_str(j, 1)

		i = int_to_two_digits_str(i)
		j = int_to_two_digits_str(j)

		trous = []

		if f"T{i_plus_1}{j}" in trou_voca :
			trous.append(f"T{i_plus_1}{j}")

		if f"T{i_moins_1}{j}" in trou_voca :
			trous.append(f"T{i_moins_1}{j}")

		if f"T{i}{j_plus_1}" in trou_voca :
			trous.append(f"T{i}{j_plus_1}")

		if f"T{i}{j_moins_1}" in trou_voca :
			trous.append(f"T{i}{j_moins_1}")

		clause = trous + [f"-{brise}"]
		gs.push_pretty_clause(clause)

	# -Tij ou B(i-1)j ou B(i+1)j ou Bi(j-1) ou Bi(j+1)
	for trou in trou_voca :

		# Soit le symbole Tij
		ij = trou[1:] # On eneleve la lettre
		i = int(ij[:2]) # On prend les deux premiers chiffres pour l'indice i
		j = int(ij[2:]) # On prend les deux derniers chiffres pour l'indice j

		i_moins_1 = int_to_two_digits_str(i, -1)
		i_plus_1 = int_to_two_digits_str(i, 1)

		j_moins_1 = int_to_two_digits_str(j, -1)
		j_plus_1 = int_to_two_digits_str(j, 1)

		i = int_to_two_digits_str(i)
		j = int_to_two_digits_str(j)

		brises = []

		if f"B{i_plus_1}{j}" in brise_voca :
			brises.append(f"B{i_plus_1}{j}")

		if f"B{i_moins_1}{j}" in brise_voca :
			brises.append(f"B{i_moins_1}{j}")

		if f"B{i}{j_plus_1}" in brise_voca :
			brises.append(f"B{i}{j_plus_1}")

		if f"B{i}{j_moins_1}" in brise_voca :
			brises.append(f"B{i}{j_moins_1}")

		clause = brises + [f"-{trou}"]
		gs.push_pretty_clause(clause)


# Si il y a un wumpus en (i, j) Alors il y a une stench en (i-1, j), (i+1, j), (i, j-1) et (i, j+1)
# Wij -> S(i-1)j ET S(i+1)j ET Si(j-1) ET Si(j+1)
# Devenant -Wij v S(i-1)j ; -Wij v S(i+1)j ; -Wij v Si(j-1) ; -Wij v Si(j+1)
# Tested and Working
def insert_wumpus_stench_regle (gs:Gophersat, wumpus_voca:List, stench_voca:List) :

	for wumpus in wumpus_voca :
		
		# Soit le symbole Tij
		ij = wumpus[1:] # On enleve la lettre
		i = int(ij[:2]) # On prend les deux premiers chiffres pour l'indice i
		j = int(ij[2:]) # On prend les deux derniers chiffres pour l'indice j

		i_moins_1 = int_to_two_digits_str(i, -1)
		i_plus_1 = int_to_two_digits_str(i, 1)

		j_moins_1 = int_to_two_digits_str(j, -1)
		j_plus_1 = int_to_two_digits_str(j, 1)

		i = int_to_two_digits_str(i)
		j = int_to_two_digits_str(j)

		stenches = []

		if f"S{i_plus_1}{j}" in stench_voca :
			stenches.append(f"S{i_plus_1}{j}")

		if f"S{i_moins_1}{j}" in stench_voca :
			stenches.append(f"S{i_moins_1}{j}")

		if f"S{i}{j_plus_1}" in stench_voca :
			stenches.append(f"S{i}{j_plus_1}")

		if f"S{i}{j_moins_1}" in stench_voca :
			stenches.append(f"S{i}{j_moins_1}")

		for stench in stenches :
			gs.push_pretty_clause([f"-{wumpus}", stench])


# On insere a chaque fin de boucle -Sij ou W(i-1)j ou W(i+1)j ou Wi(j-1) ou Wi(j+1)
# Tested and Working
def insert_stench_regle (gs:Gophersat, wumpus_voca:List, stench_voca:List) :
		
	for stench in stench_voca :
		
		# Soit le symbole Wij
		ij = stench[1:] # On enleve la lettre
		i = int(ij[:2]) # On prend les deux premiers chiffres pour l'indice i
		j = int(ij[2:]) # On prend les deux derniers chiffres pour l'indice j

		i_moins_1 = int_to_two_digits_str(i, -1)
		i_plus_1 = int_to_two_digits_str(i, 1)

		j_moins_1 = int_to_two_digits_str(j, -1)
		j_plus_1 = int_to_two_digits_str(j, 1)

		i = int_to_two_digits_str(i)
		j = int_to_two_digits_str(j)

		wumpuses = []

		if f"W{i_plus_1}{j}" in wumpus_voca :
			wumpuses.append(f"W{i_plus_1}{j}")

		if f"W{i_moins_1}{j}" in wumpus_voca :
			wumpuses.append(f"W{i_moins_1}{j}")

		if f"W{i}{j_plus_1}" in wumpus_voca :
			wumpuses.append(f"W{i}{j_plus_1}")

		if f"W{i}{j_moins_1}" in wumpus_voca :
			wumpuses.append(f"W{i}{j_moins_1}")

		clause = wumpuses + [f"-{stench}"]
		gs.push_pretty_clause(clause)


# Prend un caractere de la chaine de description d'une case et la position du contenu
# Retourne un Tuple avec les clauses a inserer dans le modèle
def wumpus_to_clause (single_case_content:str, position:Tuple[str, str]) :
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

def push_clause_from_wumpus (gs:Gophersat, case_contents:str, position:Tuple[str, str], is_from_know_method:bool = False, enable_log:bool = False):

	if enable_log :
		print(f"contents is : {case_contents}")

	facts = []
	for case_content in case_contents :
		
		if enable_log :
			print(f"inserting from wumpus : {case_content}\n")
		
		tmp_facts = wumpus_to_clause(case_content, position)
		
		if tmp_facts == -1 :
			print("Error : Invalid case contents : wumpus to clause")
			return -1
		else :
			facts = facts + tmp_facts	

	if is_from_know_method == False : # Si on utilise pas la methode know, on est certains de ce qu'il n'y a pas dans la case
		facts = facts + get_implicit_negative_facts(facts, position)

	for fact in facts : # On doit inserer les clauses une a une
		gs.push_pretty_clause([fact])

# On ajoute les faits perçu de par leur non-presence
# Exemple : On repere Bij, cela veut dire qu'il n'a pas de wumpus, ni de trou, ni de stench etc....
def get_implicit_negative_facts (facts:List, position:Tuple[str, str]) :
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
def is_wumpus_possible(gs, position:Tuple[str, str]) -> bool :
	gs.push_pretty_clause([f"W{position[0]}{position[1]}"])
	res = gs.solve()

	gs.pop_clause()

	return res

def is_trou_possible(gs, position:Tuple[str, str]) -> bool :
	gs.push_pretty_clause([f"T{position[0]}{position[1]}"])

	res = gs.solve()

	gs.pop_clause()

	return res

def idx_str_op (i_str:str, number_to_apply:int) -> str :
	
	i = int(i_str)

	i = i + number_to_apply

	if(i < 10) :
		return f"0{i}"
	else :
		return f"{i}"

# si le wumpus est possible en (i, j)
# on regarde si il possible en [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
# Si il n'est pas possible a ces coord, alors il est obligatoirement au seul endroit possible
def is_wumpus_mandatory(gs, position:Tuple[str, str], wumpus_voca) -> bool :
	i = position[0]
	j = position[1]

	pos_to_test = [
		f"W{idx_str_op(i, -1)}{idx_str_op(j, -1)}",
		f"W{idx_str_op(i, -1)}{idx_str_op(j, 1)}",
		f"W{idx_str_op(i, 1)}{idx_str_op(j, -1)}",
		f"W{idx_str_op(i, 1)}{idx_str_op(j, 1)}"
	]

	res = []
	for pos in pos_to_test :
		if pos in wumpus_voca :
			gs.push_pretty_clause([pos])
			res.append(gs.solve())
			gs.pop_clause()

	for possibility in res :
		if possibility :
			return False;

	return True;

def get_brises_to_test (carte, i:str, j:str) -> Tuple :
	
	b_tmp = [
		[int(i)-1, int(j)], # On regarde derriere la case et en haut, on ne peut connaitre qu'eux
		[int(i), int(j)-1]
	]

	b_to_test = []
	for b in b_tmp :
		if b[0] > -1 and b[1] > -1 :
			if "B" in carte[b[0]][b[1]] :
				b_to_test.append(b)

	return b_to_test

# On recupere toutes les cases autours de la brise qui ne sont pas la position que l'on teste
def get_pit_to_test (brise_pos:Tuple, i:str, j:str, taille_grille:int) -> Tuple :

	pit_tmp = [
			[brise_pos[0]-1, brise_pos[1]],
			[brise_pos[0], brise_pos[1]-1],
			[brise_pos[0]+1, brise_pos[1]],
			[brise_pos[0], brise_pos[1]+1]
		]

	pit_to_test = []
	for p in pit_tmp :
		if p[0] > -1 and p[1] > -1 :
			if p[0] < taille_grille and p[1] < taille_grille :
				if p[0] != int(i) or p[1] != int(j) :
					pit_to_test.append(p)

	return pit_to_test


def is_trou_mandatory(gs, position:Tuple[str, str], trou_voca, carte, taille_grille) -> bool :

	i = position[0]
	j = position[1]

	b_to_test = get_brises_to_test(carte, i, j)

	if len(b_to_test) < 2 : return False # Si il n'y a qu'une brise autour (ou moins), on ne peut pas savoir si c'est obligatoire

	for b in b_to_test : # On regarde autour des brises si il existe des trous auxquels ils correspondent
		
		pit_to_test = get_pit_to_test(b, i, j, taille_grille)

		# On va regarder si il existe un trou dans les positions récuperées
		# Si il en existe au moins un, l'obligation de trou dans la position [i, j] est compromise
		# il faut donc faire attention
		# Sinon, le trou est obligatoirement là
		for p in pit_to_test :
			if "P" in carte[p[0]][p[1]] :
				return False

	return True


def should_I_be_cautious (gs:Gophersat, position:Tuple[str, str], enable_log:bool = False) -> bool :

	if enable_log :
		print(f"wumpus possible : {is_wumpus_possible(gs, position)} ----- trou possible : {is_trou_possible(gs, position)}")

	return is_wumpus_possible(gs, position) or is_trou_possible(gs, position)

def print_case_contents_post_insertion (i:int, j:int, case_contents, wwr:WumpusWorldRemote, solvability:bool) :
	print(f"[{i}, {j}] - case_contents : {case_contents}")
	print(f"Satisfiabilité : {solvability}")
	print("\n --- \n")

def init_res (taille_grille) -> Tuple[Tuple] :
	return [['?' for j in range(taille_grille)] for i in range(taille_grille)]

def cartographier (wwr:WumpusWorldRemote, taille_grille:int = 4, enable_log:bool = False):

	wumpus_voca = generate_wumpus_voca(taille_grille)
	gold_voca = generate_gold_voca(taille_grille)
	stench_voca = generate_stench_voca(taille_grille)
	brise_voca = generate_brise_voca(taille_grille)
	trou_voca = generate_trou_voca(taille_grille)

	voc = wumpus_voca + gold_voca + stench_voca + brise_voca + trou_voca

	gs = Gophersat(gophersat_exec, voc)

	res = init_res(taille_grille)

	# On modelise les regles
	insert_all_regles(gs, wumpus_voca, trou_voca, brise_voca, stench_voca)

	if(gs.solve() and enable_log) :
		print(f"vocabulaire inseré sans contradiction")
		print(wwr)
	elif (gs.solve() == False) :
		print(f"contradiction dans le vocabulaire inseré")
		return -1

	if(enable_log) :
		print("\nBefore loop log :\n")
		print(f"{gs.solve()}")
		print(f"{gs.get_pretty_model()}")
		print("\n==========================\n")

	i_str = ""
	j_str = ""

	status, percepts, cost = wwr.probe(0,0)
	print(status, percepts, cost)
	res[0][0] = percepts
	is_from_know_method = False
	push_clause_from_wumpus(gs, percepts, ["00", "00"], is_from_know_method, False)

	for i in range(taille_grille) :
		for j in range(taille_grille) :
			if i != 0 or j != 0 :

				i_str = int_to_two_digits_str(i)
				j_str = int_to_two_digits_str(j)

				if is_wumpus_possible(gs, [i_str, j_str]) :
					if is_wumpus_mandatory(gs, [i_str, j_str], wumpus_voca) :
						
						status, percepts, cost = wwr.know_wumpus(i,j)
						if percepts == "Correct wumpus position." :
							percepts = "W"
							is_from_know_method = True

					else :
						status, percepts, cost = wwr.cautious_probe(i, j)

				elif is_trou_possible(gs, [i_str, j_str]) :
					if is_trou_mandatory(gs, [i_str, j_str], trou_voca, res, taille_grille) :
						
						status, percepts, cost = wwr.know_pit(i,j)
						if percepts == "Correct pit position." :
							percepts = "P"
							is_from_know_method = True

					else :
						status, percepts, cost = wwr.cautious_probe(i, j)

				else :
					status, percepts, cost = wwr.probe(i,j)

				if enable_log :
					print(status, percepts, cost, i, j)

				res[i][j] = percepts

				if(push_clause_from_wumpus(gs, percepts, [i_str, j_str], is_from_know_method, False) == -1) : # Si erreur lors de l'insertion de clauses on arrete tout : on fausse le modele
					gs.solve()
					print(f"Modele :\n {gs.get_pretty_model()} \n ---")
					return -1

				is_from_know_method = False

				if(enable_log) :
					print_case_contents_post_insertion(i, j, percepts, wwr, gs.solve())
	
	if (gs.solve() == False) :
		return -1

	if(enable_log) :
		print("\n\n==========================")

		print(f"Satisfiabilité : {gs.solve()}")
		print(f"Modele trouvé :\n {gs.get_pretty_model()} \n ---")

	return res

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
	
	status, msg, taille_grille = wwr.next_maze()
	res = cartographier(wwr, taille_grille, True)
	if(res == -1) :
			print(f"echec sur une taille de : {taille_grille}x{taille_grille}")
			sys.exit(-1)

	print(res)