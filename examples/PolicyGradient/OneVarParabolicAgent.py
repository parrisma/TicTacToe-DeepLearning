import logging
import random

from reflrn.Interface.Agent import Agent
from reflrn.Interface.ExplorationPlay import ExplorationPlay
from reflrn.Interface.Policy import Policy
from reflrn.Interface.State import State
from reflrn.exceptions import EvaluationException


class OneVarParabolicAgent(Agent):

    def __init__(self,
                 agent_id: int,  # immutable & unique id for this agent
                 agent_name: str,  # immutable & unique name for this agent
                 policy: Policy,  # the policy to drive action selection.
                 epsilon_greedy: float,  # if random() > epsilon greedy take greedy action else random action
                 exploration_play: ExplorationPlay,  # Play to take when exploring (i.e. when not being greedy)
                 lg: logging):
        self.__lg = lg
        self.__id = agent_id
        self.__name = agent_name
        self.__policy = policy
        self.__epsilon_greedy = epsilon_greedy
        self.__exploration = exploration_play

        self.__explain = None
        self.explain = False

        return

    # Return immutable id
    #
    def id(self):
        return self.__id

    # Return immutable name
    #
    def name(self):
        return self.__name

    #
    # Environment call back when environment shuts down
    #
    def terminate(self,
                  save_on_terminate: bool = False):
        if save_on_terminate:
            self.__policy.save()
        return

    #
    # Environment call back when episode starts
    #
    def episode_init(self, state: State):
        return

    #
    # Environment call back when episode is completed
    #
    def episode_complete(self, state: State):
        return

    #
    # Environment call back to ask the agent to chose an action
    #
    # State : The current representation of the environment
    # possible_actions : The set of possible actions the agent can play from this curr_coords
    #
    def choose_action(self, state: State, possible_actions: [int]) -> int:

        # if random() > epsilon greedy then take greedy action else a random action
        if random.random() > self.__epsilon_greedy:
            try:
                action = self.__policy.select_action(self.__name, state, possible_actions)
                if self.explain:
                    self.__lg.debug(self.__name + " chose greedy action : " + str(action))
            except EvaluationException:
                raise OneVarParabolicAgent.FailedToPredictActionFromPolicy()
        else:
            action = self.__exploration.select_action(possible_actions)
            if self.explain:
                self.__lg.debug(self.__name + " chose exploration action : " + str(action))

        return action

    #
    # Environment call back to reward agent for a play chosen for the given
    # curr_coords passed.
    #
    def reward(self, state: State, next_state: State, action: int, reward_for_play: float, episode_complete: bool):
        self.__policy.update_policy(self.name(),
                                    state,
                                    next_state,
                                    action,
                                    reward_for_play,
                                    episode_complete)
        return

    #
    # Called by the environment *once* at the start of the session
    # and the action set is given as dictionary
    #
    def session_init(self,
                     actions: dict) -> None:
        return

    # Failed to predict action from model
    #
    class FailedToPredictActionFromPolicy(Exception):
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

    @property
    def explain(self) -> bool:
        return self.__explain

    @explain.setter
    def explain(self, value: bool):
        if type(value) != bool:
            raise TypeError("explain property is type bool cannot not [" + type(value).__name__ + "]")
        self.__explain = value
        self.__policy.explain = True
        return
