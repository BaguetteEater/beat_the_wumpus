from lib.wumpus_client import WumpusWorldRemote
from pprint import pprint
from requests.exceptions import HTTPError

__author__ = "Sylvain Lagrue"
__copyright__ = "Copyright 2020, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.1"
__maintainer__ = "Sylvain Lagrue"
__email__ = "sylvain.lagrue@utc.fr"
__status__ = "dev"


def test_remote3():
    # Connexion au server
    server = "http://localhost:8080"
    groupe_id = "Binôme de projet 3615"  # votre vrai numéro de groupe
    names = "Khaled et Sylvain"  # vos prénoms et noms

    try:
        wwr = WumpusWorldRemote(server, groupe_id, names)
        # version pour avoir les logs de requêtes
        # wwr = WumpusWorldRemote(server, groupe_id, names, log=True)
    except HTTPError as e:
        print(e)
        print("Try to close the server (Ctrl-C in terminal) and restart it")
        return

    # Création du labyrinthe
    status, msg, size = wwr.next_maze()
    print(wwr.get_status())
    pprint(wwr.get_gold_infos())

    # Cartographie
    res = wwr.know_wumpus(1, 3)
    print(res)

    res = wwr.know_pit(2, 1)
    print(res)

    for i in range(size):
        for j in range(size):
            if (i, j) in [(1, 3), (2, 1)]:
                continue
            res = wwr.probe(i, j)
            print(res)

    status, msg = wwr.end_map()
    print(msg)
    pprint(wwr.get_gold_infos())

    # Récupération de l'or !
    path = [(0, 1), (1, 1), (1, 2), (2, 2), (1, 2), (1, 1), (0, 1), (0, 0)]

    for i, j in path:
        res = wwr.go_to(i, j)
        print(res)

    print(wwr.get_status())

    res = wwr.maze_completed()
    print(res)


if __name__ == "__main__":
    test_remote3()

