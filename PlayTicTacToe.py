import numpy as np
import random
from random import randint
from TicTacToe import TicTacToe


class PlayTicTacToe:

    __learning_rate_0 = 0.05
    __learning_rate_decay = 0.001
    __discount_factor = .8
    __q_values = {}  # learning spans game sessions.

    #
    # Constructor has no arguments as it just sets the game
    # to an initial up-played set-up
    #
    def __init__(self, persist):
        self.__game = TicTacToe()
        self.__persist = persist

    #
    # Return the current game
    #
    def game(self):
        return self.__game

    #
    # Set learned state to given QValues.
    #
    def transfer_learning(self, qv):
        self.__q_values = qv
        print("Learned Games:" + str(len(self.__q_values)))

    #
    # The learned Q Values for a given state if they exist
    #
    def q_vals_for_state(self, state):
        if state in self.__q_values:
            return self.__q_values[state]
        else:
            return None

    #
    # Expose the current class instance learning in terms of Q Values.
    #
    def q_vals(self):
        return self.__q_values

    #
    # Load Q Val state
    #
    def load_q_vals(self, filename):
        self.__q_values = self.__persist.load(filename)
        return

    #
    # Save Q Val state
    #
    def save_q_vals(self, filename):
        self.__persist.save(self.__q_values, filename)
        return

    #
    # Forget learning
    #
    def forget_learning(self):
        self.__q_values = dict()

    #
    # Add states to Q Value dictionary if not present
    #
    def add_states_if_missing(self, state):
        if state not in self.__q_values:
            self.__q_values[state] = TicTacToe.empty_board()
            np.reshape(self.__q_values[state], self.__q_values[state].size)  # flatten

    #
    # Return the learning rate paramaters
    #
    @classmethod
    def learning_rate_params(cls):
        return cls.__learning_rate_0, cls.__learning_rate_decay, cls.__discount_factor

    #
    # Return the learning rate based on number of learnings to date
    #
    @classmethod
    def q_learning_rate(cls, n):
        return cls.__learning_rate_0 / (1 + (n * cls.__learning_rate_decay))

    #
    # Return the State, Action Key from the perspective of given player
    #
    @classmethod
    def state(cls, player, board):
        sa = ""
        sa += str(player)
        for cell in np.reshape(board, TicTacToe.num_actions()).tolist(): sa += str(TicTacToe.player_to_int(cell))
        return sa

    #
    # Given q values for play_action to a given state select the
    # as to maximise players gain or if not gain to be had
    # minimise opponents gain
    #
    @classmethod
    def best_outcome(cls, q):
        return cls.best_move(q)

    #
    # The best play_action is to play to win if there is an option to do so
    # or to play defensively and minimise (block) the biggest gain of
    # the opponent.
    #
    @classmethod
    def best_move(cls, q):
        q = q[np.isnan(q) == False]
        if len(q) > 0:
            stand_to_win = np.max(q)
            stand_to_lose = np.min(q)
            if stand_to_win > 0:
                return stand_to_win
            else:
                return stand_to_lose
        else:
            return np.nan

    #
    # Return zero float if given number is "nan"
    #
    @classmethod
    def zero_if_nan(cls, n):
        if np.isnan(n):
            return 0
        else:
            return n

    #
    # Run simulation to estimate Q values for state, action pairs. Random exploration policy
    # which should be tractable with approx 6K valid board states. This function takes "canned"
    # moves which were full game sequences created else where.
    #
    def train_q_values(self, num_episodes, canned_moves):

        # Simulation defaults.
        learning_rate0, learning_rate_decay, discount_rate = PlayTicTacToe.learning_rate_params()

        # Initialization
        reward = 0
        sim = 0
        game_step = 0

        # Iterate over and play
        while sim < num_episodes:
            self.__game.reset()
            plyr = None
            prev_plyr = None
            s = None
            mv = None
            prev_mv = None
            prev_s = None
            mv = None

            game_step = 0
            while not self.__game.game_over():

                prev_mv = mv
                print(str(sim) + " : " + str(game_step))
                plyr, mv = (canned_moves[sim])[game_step]
                prev_plyr = TicTacToe.other_player(plyr)
                prev_s = s

                s = PlayTicTacToe.state(plyr, self.__game.board())
                reward = self.__game.play_action(mv, plyr)
                learning_rate = PlayTicTacToe.q_learning_rate(len(self.__q_values))

                self.add_states_if_missing(s)

                # Update Q Values for both players based on last play reward.
                (self.__q_values[s])[mv - 1] = (learning_rate * (self.zero_if_nan(self.__q_values[s][mv - 1]))) + ((1 - learning_rate) * reward[0])
                if prev_s is not None:
                    (self.__q_values[prev_s])[prev_mv - 1] -= (discount_rate * self.best_outcome(self.__q_values[s]))
                game_step += 1
            sim += 1
            game_step = 0

            if ((sim % 1000) == 0) or (sim == num_episodes):
                print("Training Cycle:" + str(sim))
        return self.__q_values

    #
    # Run simulation to estimate Q values for state, action pairs. Random exploration policy
    # which should be tractable with approx 6K valid board states.
    #
    def train_q_values_r(self, num_simulations):

        learning_rate0, learning_rate_decay, discount_rate = PlayTicTacToe.learning_rate_params()

        reward = 0
        sim = 0
        game_step = 0

        while sim < num_simulations:
            self.__game.reset()
            plyr = None
            s = None
            mv = None
            prev_mv = None
            prev_s = None

            plyr = (TicTacToe.player_X, TicTacToe.player_O)[randint(0, 1)]  # Random player to start

            mv = None
            while not self.__game.game_over():

                prev_mv = mv
                st = PlayTicTacToe.state(plyr, self.__game.board())
                if random.random() > 0.8:
                    mv = self.informed_move(st, False)  # Informed Player
                else:
                    mv = self.informed_move(st, True)  # Random Player

                prev_s = s
                s = PlayTicTacToe.state(plyr, self.__game.board())
                reward = self.__game.play_action(mv, plyr)
                learning_rate = PlayTicTacToe.q_learning_rate(len(self.__q_values))

                self.add_states_if_missing(s)

                # Update Q Values for both players based on last play reward.
                (self.__q_values[s])[mv - 1] = (learning_rate * (self.zero_if_nan(self.__q_values[s][mv - 1]))) + ((1 - learning_rate) * reward[0])
                if prev_s is not None:
                    (self.__q_values[prev_s])[prev_mv - 1] -= (discount_rate * self.best_outcome(self.__q_values[s]))

                plyr = TicTacToe.other_player(plyr)
                game_step += 1
            sim += 1
            game_step = 0

            if ((sim % 1000) == 0) or (sim == num_simulations):
                print("Training Cycle:" + str(sim))
        return self.__q_values

    #
    # Given current state and learned Q Values (if any) suggest
    # the play_action that is expected to yield the highest reward.
    #
    def informed_move(self, st, rnd):
        # What moves are possible at this stage
        valid_moves = self.__game.what_are_valid_moves()

        # Are there any moves ?
        if np.sum(valid_moves * np.full(TicTacToe.num_actions(), 1)) == 0:
            return None

        best_action = None
        if not rnd:
            # Is there info learned for this state ?
            informed_actions = self.q_vals_for_state(st)
            if informed_actions is not None:
                informed_actions *= valid_moves
                best_action = PlayTicTacToe.best_move(informed_actions)
                informed_actions = (informed_actions == best_action)*TicTacToe.actions()
                informed_actions = informed_actions[np.where(informed_actions!=0)]
                if informed_actions.size > 0:
                    best_action = informed_actions[randint(0, informed_actions.size - 1)]
                else:
                    best_action = None

        # If we found a good action then return that
        # else pick a random action
        if best_action is None:
            actions = valid_moves * np.arange(1, TicTacToe.num_actions() + 1, 1)
            actions = actions[np.where(actions > 0)]
            best_action = actions[randint(0, actions.size - 1)]

        return int(best_action)
        #

    # Play an automated game between a random player and an
    # informed player.
    # Return the play_action sequence for the entire game as s string.
    #
    def play(self):
        self.__game.reset()
        plyr = (TicTacToe.player_X, TicTacToe.player_O)[randint(0, 1)]  # Chose random player to start
        mv = None
        game_moves_as_str = ""
        while not self.__game.game_over():
            st = PlayTicTacToe.state(plyr, self.__game.board())
            if plyr == TicTacToe.player_X:
                mv = self.informed_move(st, False)  # Informed Player
            else:
                mv = self.informed_move(st, True)  # Random Player
            self.__game.play_action(mv, plyr)
            game_moves_as_str += str(plyr) + ":" + str(mv) + "~"
            plyr = TicTacToe.other_player(plyr)
        return game_moves_as_str

    #
    # Add the game profile to the given game dictionary and
    # up the count for the number of times that games was played
    #
    @classmethod
    def record_game_stats(cls, game_stats_dict, profile):
        if profile in game_stats_dict:
            game_stats_dict[profile] += 1
        else:
            game_stats_dict[profile] = 1
        return

    def play_many(self, num):
        informed_wins = 0
        random_wins = 0
        draws = 0
        I = {}
        R = {}
        D = {}
        G = {}
        profile = ""
        for x in range(0, num):
            profile = self.play()
            if profile not in G: G[profile] = ""
            if self.__game.game_won(self.__game.board(), TicTacToe.player_X):
                informed_wins += 1
                PlayTicTacToe.record_game_stats(I, profile)
            else:
                if self.__game.game_won(self.__game.board(), TicTacToe.player_O):
                    random_wins += 1
                    PlayTicTacToe.record_game_stats(R, profile)
                else:
                    PlayTicTacToe.record_game_stats(D, profile)
                    draws += 1
            if (x % 100) == 0:
                print(str(x))
        print("Informed :" + str(informed_wins) + " : " + str(round((informed_wins / num) * 100, 0)))
        print("Random :" + str(random_wins) + " : " + str(round((random_wins / num) * 100, 0)))
        print("Draw :" + str(draws) + " : " + str(round((draws / num) * 100, 0)))
        print("Diff Games :" + str(len(G)))
        return I, R, D

    #
    # Convert a game profile string returned from play method
    # into an array that can be passed as a canned-play_action to
    # training. (Q learn)
    #
    @classmethod
    def string_of_moves_to_array(cls, moves_as_str):
        mvd = {}
        mvc = 0
        mvs = moves_as_str.split('~')
        for mv in mvs:
            if len(mv) > 0:
                pl, ps = mv.split(":")
                mvd[mvc] = (int(pl), int(ps))
            mvc += 1
        return mvd

    #
    # Convert a game profile string returned from play method
    # into an array that can be passed as a canned-play_action to
    # training. (Q learn)
    #
    @classmethod
    def string_of_moves_to_a_board(cls, moves_as_str):
        mvc = 0
        mvs = moves_as_str.split('~')
        bd = np.reshape(TicTacToe.empty_board(),TicTacToe.num_actions())
        for mv in mvs:
            if len(mv) > 0:
                pl, ps = mv.split(":")
                bd[int(ps) - 1] = int(pl)
            mvc += 1
        return np.reshape(bd, (3, 3))

    #
    # Convert a dictionary of game profiles returned from play_many
    # to a dictionary of canned moves that can be passed to training (Q Learn)
    #
    @classmethod
    def moves_to_dict(cls, move_dict):
        md = {}
        i = 0
        for mvss, cnt in move_dict.items():
            md[i] = PlayTicTacToe.string_of_moves_to_array(mvss)
            i += 1
        return md

    #
    # All possible endings. Generate moves str's for all the possible endings of the
    # game from the perspective of the prev player.
    #
    # The given moves must be the moves of a valid game that played to either win/draw
    # including the last play_action that won/drew the game.
    #
    @classmethod
    def all_possible_endings(cls, moves_as_str, exclude_current_ending=True):
        ape = {}
        mvs = PlayTicTacToe.string_of_moves_to_array(moves_as_str)

        terminal_move = mvs[len(mvs) - 1]  # The play_action that won, drew
        last_move = mvs[len(mvs) - 2]  # the play_action we will replace with all other options

        t_plyr = terminal_move[0]
        t_actn = terminal_move[1]

        l_plyr = last_move[0]
        l_actn = last_move[1]

        base_game = "~".join(moves_as_str.split("~")[:-3])  # less Trailing ~ + terminal & last play_action
        bd = PlayTicTacToe.string_of_moves_to_a_board(base_game)
        vmvs = TicTacToe.valid_moves(bd)
        a = 1
        for vm in vmvs:
            poss_end = base_game
            if vm:
                if a != t_actn:  # don't include the terminal action as we will add that back on.
                    if not (exclude_current_ending and a == l_actn):
                        poss_end += "~" + str(l_plyr) + ":" + str(a)
                        poss_end += "~" + str(t_plyr) + ":" + str(t_actn) + "~"
                        ape[poss_end] = 0
            a += 1
        return ape

    #
    # Make a play based on q values (called via interactive game)
    #
    def machine_move(self):
        st = PlayTicTacToe.state(TicTacToe.player_X, self.game().board())
        qv = self.q_vals_for_state(st)
        print(TicTacToe.board_as_string(self.game().board(), qv))
        mv = self.informed_move(st, False)
        self.game().play_action(mv, TicTacToe.player_X)
        return str(TicTacToe.player_X)+":"+str(mv)+"~"

    #
    # Make a play based on human input  (called via interactive game)
    #
    def human_move(self):
        st = PlayTicTacToe.state(TicTacToe.player_O, self.game().board())
        qv = self.q_vals_for_state(st)
        print(TicTacToe.board_as_string(self.game().board(), qv))
        mv = input("Make your play_action: ")
        self.game().play_action(int(mv), TicTacToe.player_O)
        return str(TicTacToe.player_O)+":"+str(mv)+"~"

    #
    # Play an interactive game with the informed player via
    # stdin.
    #
    def interactive_game(self, human_first):
        self.__game.reset()
        mvstr = ""

        player_move = dict()
        if human_first:
            player_move[1] = PlayTicTacToe.human_move
            player_move[2] = PlayTicTacToe.machine_move
        else:
            player_move[1] = PlayTicTacToe.machine_move
            player_move[2] = PlayTicTacToe.human_move

        while not self.__game.game_over():
            mvstr += player_move[1](self)
            if self.__game.game_over():
                break
            mvstr += player_move[2](self)

        print("Game Over")