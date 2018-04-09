import numpy as np
from .Grid import Grid
from .IllegalGridMoveException import IllegalGridMoveException
from copy import deepcopy

#
# Simple (small grid) with the basic North, South, East, West moves (no diagonal moves)
# The grid map of rewards is defined at construction time.
#
#


class SimpleGridOne(Grid):

    STEP = np.float(-1)
    FIRE = np.float(-100)
    GOAL = np.float(+100)
    BLCK = np.float(-101)
    FREE = np.float(0)
    NORTH = np.int(0)
    SOUTH = np.int(1)
    EAST = np.int(3)
    WEST = np.int(4)
    __actions = dict()
    __actions = {NORTH: (1, 0), SOUTH: (-1, 0), EAST: (0, 1), WEST: (0, -1)}  # N, S ,E, W (row-offset, col-offset)

    def __init__(self,
                 grid_id: int,
                 grid_map: [],
                 start_coords: (),
                 finish_coords: ()
                 ):
        self.__grid_id = grid_id
        self.__grid = grid_map[:]  # Deep Copy
        self.__grid_rows = len(self.__grid)
        self.__grid_cols = len(self.__grid[0])
        self.__start = deepcopy(start_coords)
        self.__finish = deepcopy(finish_coords)
        self.__curr = (self.__start[0], self.__start[1])

    def execute_action(self, action: int) -> int:
        if action not in self.allowable_actions():
            raise IllegalGridMoveException("Illegal Move on Grid as target cell blocked")

        self.__curr = self.__move(action)
        return self.__grid_reward(self.__curr)

    def actions(self) -> [int]:
        return self.__actions.copy()

    def id(self) -> int:
        return self.__grid_id

    def copy(self) -> Grid:
        cp = type(self)(self.id(),
                        self.__grid,
                        self.__start,
                        self.__finish)
        cp.__curr = self.__curr
        return cp

    def __move(self, action: int) -> ():
        return self.__curr + self.__actions[action]

    def __grid_reward(self, coords: ()) -> np.float:
        return self.__grid[coords[0]][coords[1]]

    def __blocked(self, coords: ()) -> bool:
        return self.__grid[coords[0]][coords[1]] == self.BLCK

    def allowable_actions(self) -> [int]:
        ams = []
        if self.__curr[0] > 0 and not self.__blocked(self.__move(self.NORTH)):
            ams.append(self.NORTH)
        if self.__curr[0] + 1 < self.__grid_rows and not self.__blocked(self.__move(self.SOUTH)):
            ams.append(self.SOUTH)
        if self.__curr[1] > 0 and not self.__blocked(self.__move(self.EAST)):
            ams.append(self.EAST)
        if self.__curr[1] + 1 < self.__grid_cols and not self.__blocked(self.__move(self.WEST)):
            ams.append(self.WEST)
        return ams
