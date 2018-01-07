import numpy as np
import sys
from random import randint


class TicTacToe:

    # There are 5812 legal board states that can be reached before there is a winner
    # http://brianshourd.com/posts/2012-11-06-tilt-number-of-tic-tac-toe-boards.html

    __bad_move_game_is_over = -1
    __bad_move_action_already_played = -2
    __bad_move_no_consecutive_plays = -3
    __play = float(0)  # reward for playing an action
    __draw = float(200)  # reward for playing to end but no one wins
    __win = float(100)  # reward for winning a game
    __loss = float(-200)  # reward (penalty) for losing a game
    __rewards = {"Play": 0, "Draw": 200, "Win": 100, "Loss": -200}
    __no_player = np.nan  # id of a non existent player i.e. used to record id of player that has not played
    __win_mask = np.full((1, 3), 3, np.int8)
    __actions = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2), 7: (2, 0), 8: (2, 1), 9: (2, 2)}
    player_X = 1  # numerical value of player X on the board
    player_O = -1  # numerical value of player O on the board
    empty_cell = np.nan  # value of a free action space on board
    asStr = True

    #
    # Return game to initial state, where no one has played
    # and the board contains no moves.
    #
    def reset(self):
        self.__board = np.full((3, 3), np.nan)
        self.__last_board = np.full((3, 3), np.nan)
        self.__game_over = False
        self.__game_drawn = False
        self.__player = TicTacToe.__no_player
        self.__last_player = TicTacToe.__no_player

    #
    # Constructor has no arguments as it just sets the game
    # to an intial up-played set-up
    #
    def __init__(self):
        self.__board = np.full((3, 3), np.nan)
        self.__last_board = np.full((3, 3), np.nan)
        self.__game_over = False
        self.__game_drawn = False
        self.__player = TicTacToe.__no_player
        self.__last_player = TicTacToe.__no_player

    #
    # Return a displayable version of the entire game.
    #
    def __str__(self):
        s = ""
        s += "Game Over: " + str(self.__game_over) + "\n"
        s += "Player :" + TicTacToe.__player_to_str(self.__player) + "\n"
        s += "Current Board : \n" + str(self.__board) + "\n"
        s += "Prev Player :" + TicTacToe.__player_to_str(self.__last_player) + "\n"
        s += "Prev Current Board : \n" + str(self.__last_board) + "\n"
        return s

    #
    # Render the board as human readable with q values adjacent if supplied
    #
    @classmethod
    def print_board(cls, bd, qv=None):
        if not qv is None : qv = np.reshape(qv, (3, 3))
        for i in range(0, 3):
            rbd = ""
            rqv = ""
            for j in range(0, 3):
                rbd += "["
                rbd += cls.__player_to_str(bd[i][j])
                rbd += "]"
                if not qv is None:
                    rqv += "["
                    rqv += cls.__single_q_value_to_str(qv[i][j])
                    rqv += "]"
            sys.stdout.write(rbd+"    "+rqv+"\n")
        sys.stdout.write("\n")
        sys.stdout.flush()

    #
    # return player as string "X" or "O"
    #
    @classmethod
    def __player_to_str(cls, player):
        if np.sum(np.isnan(player)*1) >0: return " "
        if player == TicTacToe.player_X: return "X"
        if player == TicTacToe.player_O: return "O"
        return " "

    #
    # return single q val as formatted float or spaces for nan
    #
    @classmethod
    def __single_q_value_to_str(cls, sqv):
        if np.sum(np.isnan(sqv)*1) >0:
                return " " * 26
        s = '{:+.16f}'.format(sqv)
        s = " "*(26-len(s))+s
        return s

    #
    # return player as integer
    #
    @classmethod
    def player_to_int(cls, player):
        if np.isnan(player):
            return 0
        return int(player)

    #
    # Return the number of possible actions as a list of integers.
    #
    @classmethod
    def num_actions(cls):
        return len(TicTacToe.__actions)

    #
    # Return the maximum number of moves per game.
    #
    @classmethod
    def max_moves_per_game(cls):
        return len(TicTacToe.__actions)

    #
    # Return the actions as a list of integers.
    #
    @classmethod
    def actions(cls):
        return list(map(lambda a: int(a), list(TicTacToe.__actions.keys())))

    #
    # Return the board index (i,j) of a given action
    #
    @classmethod
    def board_index(cls, action):
        return TicTacToe.__actions[action]

    #
    # Return rewards as dictionary where key is name of reward
    # and the value is the reward
    #
    @classmethod
    def rewards(cls):
        return TicTacToe.__rewards

    #
    # Assume the move has been validated by move method
    # Make a copy of board before move is made and the last player
    #
    def __make_move(self, action, player):
        self.__last_board = np.copy(self.__board)
        self.__last_player = self.__player
        self.__player = player
        self.__board[TicTacToe.board_index(action)] = player
        return

    #
    # Has a player already moved using the given action.
    #
    def __invalid_move(self, action):
        return not np.isnan(self.__board[TicTacToe.board_index(action)])

    #
    # If the proposed action is a valid move and the game is not
    # over. Make the given move (action) on behalf of the given
    # player and update the game status.
    #
    # return the rawards (Player who took move, Observer)
    #
    def move(self, action, player):
        if TicTacToe.game_won(self.__board): return TicTacToe.__bad_move_game_is_over
        if self.__invalid_move(action): return TicTacToe.__bad_move_action_already_played
        if player == self.__player: return TicTacToe.__bad_move_no_consecutive_plays

        self.__make_move(action, player)

        if (TicTacToe.game_won(self.__board)):
            self.__game_over = True
            self.__game_drawn = False
            return np.array([TicTacToe.__win, TicTacToe.__loss])

        if (not TicTacToe.moves_left_to_take(self.__board)):
            self.__game_over = True
            self.__game_drawn = True
            return np.array([TicTacToe.__draw, TicTacToe.__draw])

        return np.array([TicTacToe.__play, 0])

    #
    # Return (flattened) Game Ended, Last Player, Last Board, Player, Board
    #
    def detailed_state(self):
        flattened_state = []
        if (self.__game_over):
            flattened_state.append(1)
        else:
            flattened_state.append(0)
        flattened_state.append(self.__last_player)
        flattened_state.append(self.__player)
        for itm in np.reshape(self.__last_board, 9).tolist(): flattened_state.append(itm)
        for itm in np.reshape(self.__board, 9).tolist(): flattened_state.append(itm)

        return flattened_state

    #
    # Show return the current board contents
    #
    def board(self):
        return self.__board

    #
    # Any row, column or diagonal with all player X or player O. If a
    # player is given then it answers has that specific player won
    #
    @classmethod
    def game_won(cls, bd, plyr=None):

        if not plyr is None: bd = (bd == plyr) * 1

        rows = np.abs(np.sum(bd, axis=1))
        cols = np.abs(np.sum(bd, axis=0))
        diag_lr = np.abs(np.sum(bd.diagonal()))
        diag_rl = np.abs(np.sum(np.rot90(bd).diagonal()))

        if np.sum(rows == 3) > 0:
            return True
        if np.sum(cols == 3) > 0:
            return True
        if not np.isnan(diag_lr):
            if ((np.mod(diag_lr, 3)) == 0) and diag_lr > 0:
                return True
        if not np.isnan(diag_rl):
            if ((np.mod(diag_rl, 3)) == 0) and diag_rl > 0:
                return True
        return False

    #
    # Are there any remaining moves to be taken >
    #
    @classmethod
    def moves_left_to_take(cls, bd):
        return bd[np.isnan(bd)].size > 0

    #
    # Board is in a gamne over state, with a winner or a draw
    #
    @classmethod
    def board_game_over(cls, board):
        return (TicTacToe.game_won(board) or not TicTacToe.moves_left_to_take(board))

    #
    # Is the game over ?
    #
    def game_over(self):
        return TicTacToe.board_game_over(self.__board)

    #
    # Return which player goes next given the current player
    #
    @staticmethod
    def other_player(current_player):
        if (current_player == TicTacToe.player_O):
            return TicTacToe.player_X
        else:
            return TicTacToe.player_O

    #
    # What moves are valid for the given board
    #
    @classmethod
    def valid_moves(cls, board):
        vm = np.isnan(board.reshape(TicTacToe.num_actions()))
        return vm

    #
    # What moves are valid given for board or if not
    # for the current game board.
    #
    def what_are_valid_moves(self):
        return TicTacToe.valid_moves(self.__board)
