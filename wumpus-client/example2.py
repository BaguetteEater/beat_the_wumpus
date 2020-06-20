from lib.wumpus_client import WumpusWorldRemote

from requests.exceptions import HTTPError

__author__ = "Sylvain Lagrue"
__copyright__ = "Copyright 2020, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Sylvain Lagrue"
__email__ = "sylvain.lagrue@utc.fr"
__status__ = "dev"


def test_remote2():
    # Connexion au server
    server = "http://localhost:8080"
    groupe_id = "Binôme de projet 3615"  # votre vrai numéro de groupe
    names = "Khaled et Sylvain"  # vos prénoms et noms

    try:
        wwr = WumpusWorldRemote(server, groupe_id, names)
    except HTTPError as e:
        print(e)
        print("Try to close the server (Ctrl-C in terminal) and restart it")
        return

    # Récupération du premier labyrinthe
    status, msg, size = wwr.next_maze()
    while status == "[OK]":
        print(msg)
        print("taille: ", size)

        ###################
        ##### PHASE 1 #####
        ###################

        status, percepts, cost = wwr.probe(0, 0)
        print(status, percepts, cost)

        status, percepts, cost = wwr.probe(0, 0)
        print(status, percepts, cost)

        # Toutes les cases doivent être connues pour finir la phase 1
        # Ci-après une méthode très couteuse pour arriver à ce résultat
        for i in range(size):
            for j in range(size):
                status, percepts, cost = wwr.cautious_probe(i, j)
                print(status, percepts, cost)

                gold = wwr.get_gold_infos()
                print(gold)

        status, msg = wwr.end_map()
        print(status, msg)

        ###################
        ##### PHASE 2 #####
        ###################

        phase, pos = wwr.get_status()
        print("status:", phase, pos)
        i, j = wwr.get_position()
        print(f"Vous êtes en ({i},{j})")

        for i, j in [
            (0, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (1, 2),
            (0, 2),
            (0, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (1, 2),
            (0, 2),
            (0, 1),
            (0, 0),
        ]:
            status, msg, cost = wwr.go_to(i, j)
            print(msg)

            gold = wwr.get_gold_infos()
            print(gold)

        res = wwr.maze_completed()
        print(res)

        phase, pos = wwr.get_status()
        print("status:", phase, pos)

        print("press enter for the next maze !!")
        input()

        status, msg, size = wwr.next_maze()


if __name__ == "__main__":
    test_remote2()
