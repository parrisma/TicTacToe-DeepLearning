import logging
import random

import numpy as np

from examples.gridworld.GridWorld import GridWorld
from examples.gridworld.GridWorldAgent import GridWorldAgent
from examples.gridworld.RenderSimpleGridOneQValues import RenderSimpleGridOneQValues
from examples.gridworld.GridWorldUnitTests.GridFactory import GridFactory
from reflrn.EnvironmentLogging import EnvironmentLogging
from reflrn.EpsilonGreedyExplorationStrategy import EpsilonGreedyExplorationStrategy
from reflrn.RandomPolicy import RandomPolicy
from reflrn.TemporalDifferenceQValPolicy import TemporalDifferenceQValPolicy

random.seed(42)
np.random.seed(42)

#
# Set Manually and re-run
#
epgrdy = 0.8
itr = 200000
lg = EnvironmentLogging("TestRig-TemporalDifference", "TestRig-TemporalDifference.log", logging.DEBUG).get_logger()
lg.setLevel('DEBUG')

test_grid = GridFactory.test_grid_five()
sh = test_grid.shape()

epsilon_greedy_strategy = EpsilonGreedyExplorationStrategy(
    greedy_policy=TemporalDifferenceQValPolicy(lg=lg,
                                               filename="./gridworld-tmpr-diff.pb",
                                               manage_qval_file=True,
                                               load_qval_file=False,
                                               save_every=100,
                                               q_val_render=RenderSimpleGridOneQValues(sh[0],
                                                                                       sh[1],
                                                                                       do_scale=False,
                                                                                       do_plot=True)
                                               ),
    exploration_policy=RandomPolicy(prefer_new=True),
    epsilon=epgrdy,
    lg=lg)

agent_x = GridWorldAgent(agent_id=1,
                         agent_name="GridAgent",
                         exploration_strategy=epsilon_greedy_strategy,
                         lg=lg)

game = GridWorld(agent_x, test_grid, lg)
game.run(itr)
