from typing import Dict, Tuple, List

__author__ = "Sylvain Lagrue"
__copyright__ = "Copyright 2019, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.3"
__maintainer__ = "Sylvain Lagrue"
__email__ = "sylvain.lagrue@utc.fr"
__status__ = "dev"


class WumpusWorld:
    def __init__(self):
        self.__knowledge = [[False] * 4 for i in range(4)]
        self.__world = [
            ["", "", "P", ""],
            ["", "", "", ""],
            ["W", "G", "P", ""],
            ["", "", "", "P"],
        ]
        self.__another_world = [
            ["", "", "", ""],
            ["P", "", "P", "W"],
            ["", "G", "P", ""],
            ["", "", "", "P"],
        ]
        self.__position = (0, 0)
        self.__dead = False
        self.__gold_found = False
        self.compute_breeze()
        self.compute_stench()
        self.compute_empty()
        self.cost = 0

    def compute_empty(self):
        for i in range(4):
            for j in range(4):
                if self.__world[i][j] == "":
                    self.__world[i][j] = "."

    def compute_breeze(self):
        for i in range(4):
            for j in range(4):
                if "P" in self.__world[i][j]:
                    if i + 1 < 4 and "B" not in self.__world[i + 1][j]:
                        self.__world[i + 1][j] += "B"
                    if j + 1 < 4 and "B" not in self.__world[i][j + 1]:
                        self.__world[i][j + 1] += "B"
                    if i - 1 >= 0 and "B" not in self.__world[i - 1][j]:
                        self.__world[i - 1][j] += "B"
                    if j - 1 >= 0 and "B" not in self.__world[i][j - 1]:
                        self.__world[i][j - 1] += "B"

    def compute_stench(self):
        for i in range(4):
            for j in range(4):
                if "W" in self.__world[i][j]:
                    if i + 1 < 4:
                        self.__world[i + 1][j] += "S"
                    if j + 1 < 4:
                        self.__world[i][j + 1] += "S"
                    if i - 1 >= 0:
                        self.__world[i - 1][j] += "S"
                    if j - 1 >= 0:
                        self.__world[i][j - 1] += "S"

    def get_knowledge(self):
        res = [["?"] * 4 for i in range(4)]

        for i in range(4):
            for j in range(4):
                if self.__knowledge[i][j]:
                    res[i][j] = self.__world[i][j]

        return res

    def get_position(self) -> Tuple[int, int]:
        return self.__position

    def get_percepts(self) -> str:
        i = self.__position[0]
        j = self.__position[1]
        self.__knowledge[i][j] = True

        return (f"[OK] you feel {self.__world[i][j]}", self.__world[i][j])

    def probe(self, i, j) -> str:
        #if i == 0 and j == 0 and self.__gold_found:
        #    return "[OK] you win !!!"

        if (
            #abs(i - self.__position[0]) + abs(j - self.__position[1]) != 1 or
            i < 0
            or j < 0
            or i >= 4
            or j >= 4
        ):
            return "[err] impossible move..."

        self.__position = (i, j)
        content = self.__world[i][j]
        if "W" in content or "P" in content:
            self.__dead = True
            self.cost += 1000
            return "[KO] The wizard catches a glimpse of the unthinkable and turns mad"
        self.cost += 10
        a,b = self.get_percepts()
        print(a)
        return b

    def __str__(self) -> str:
        s = ""
        for i in range(4):
            s += f"{i}:"
            for j in range(4):
                s += f" {self.__world[i][j]} "
            s += "\n"

        return s


if __name__ == "__main__":
    ww = WumpusWorld()
    print(ww.get_percepts())
    print(ww.go_to(0, 1))
    print(ww.get_percepts())
    print(ww.get_position())
    print(ww.go_to(0, 2))

    print(ww)
