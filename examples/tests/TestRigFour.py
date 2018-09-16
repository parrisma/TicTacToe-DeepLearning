import logging

from examples.tictactoe.TicTacToe import TicTacToe
from examples.tictactoe.TicTacToeAgent import TicTacToeAgent
from reflrn.EnvironmentLogging import EnvironmentLogging
from reflrn.PureRandomExploration import PureRandomExploration
from reflrn.RandomPolicy import RandomPolicy
from reflrn.TemporalDifferenceDeepNNPolicy import TemporalDifferenceDeepNNPolicy

itr = 5000
lg = EnvironmentLogging("TestRig4", "TestRigFour.log", logging.INFO).get_logger()

tddnnp = TemporalDifferenceDeepNNPolicy(lg=lg)
tddnnp.load('model.keras')

agent_x = TicTacToeAgent(1,
                         "X",
                         RandomPolicy(),
                         epsilon_greedy=0,
                         exploration_play=PureRandomExploration(),
                         lg=lg)

agent_o = TicTacToeAgent(-1,
                         "O",
                         RandomPolicy(),
                         epsilon_greedy=0,
                         exploration_play=PureRandomExploration(),
                         lg=lg)

game = TicTacToe(agent_x, agent_o, lg)
game.run(itr)
