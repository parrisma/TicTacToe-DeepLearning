import logging
import random

import numpy as np

from examples.tictactoe.TicTacToe import TicTacToe
from examples.tictactoe.TicTacToeAgent import TicTacToeAgent
from examples.tictactoe.TicTacToeNN import TicTacToeNN
from reflrn.ActorCriticPolicyTDQVal import ActorCriticPolicyTDQVal
# from reflrn.DequeReplayMemory import DequeReplayMemory
from reflrn.EnvironmentLogging import EnvironmentLogging
from reflrn.GeneralModelParams import GeneralModelParams
from reflrn.HumanPolicy import HumanPolicy
from reflrn.Interface.ModelParams import ModelParams
from reflrn.PureRandomExploration import PureRandomExploration

# from reflrn.SimpleRandomPolicyWithReplayMemory import SimpleRandomPolicyWithReplayMemory

random.seed(42)
np.random.seed(42)

itr = 20000
lg = EnvironmentLogging("ActorCriticTicTacToe", "ActorCriticTicTacToe.log", logging.INFO).get_logger()

load = False

pp = GeneralModelParams([[ModelParams.epsilon, float(.80)],
                         [ModelParams.epsilon_decay, float(0)],
                         [ModelParams.num_actions, int(9)],
                         [ModelParams.model_file_name, 'TicTacToe-ActorCritic'],
                         [ModelParams.verbose, int(0)],
                         [ModelParams.num_states, int(5500)]
                         ])

nn = TicTacToeNN(pp.get_parameter(ModelParams.num_actions),
                 pp.get_parameter(ModelParams.num_actions))

acp = ActorCriticPolicyTDQVal(policy_params=pp,
                              network=nn,
                              lg=lg)
if load:
    acp.load('ActorCriticPolicy')

agent_x = TicTacToeAgent(1,
                         "X",
                         acp,
                         epsilon_greedy=0,
                         exploration_play=PureRandomExploration(),
                         lg=lg)

# srp = SimpleRandomPolicyWithReplayMemory(lg, DequeReplayMemory(lg, 500))
srp = ActorCriticPolicyTDQVal(policy_params=pp,
                              network=nn,
                              lg=lg)
agent_o = TicTacToeAgent(-1,
                         "O",
                         srp,
                         epsilon_greedy=0,
                         exploration_play=PureRandomExploration(),
                         lg=lg)

if not load:
    game = TicTacToe(agent_x, agent_o, lg)
    acp.link_to_env(game)
    srp.link_to_env(game)
    acp.explain = False
    srp.explain = False
    game.run(itr)

lg.level = logging.DEBUG
itr = 100
hum = HumanPolicy("o", lg)
agent_h = TicTacToeAgent(-1,
                         "O",
                         hum,
                         epsilon_greedy=0,
                         exploration_play=PureRandomExploration(),
                         lg=lg)

game2 = TicTacToe(agent_x, agent_h, lg)
if load:
    acp.link_to_env(game2)
hum.link_to_env(game2)
acp.explain = True
acp.exploration_off()
game2.run(itr)
