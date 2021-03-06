import abc

from reflrn.Interface.Agent import Agent
from reflrn.Interface.State import State


#
# This abstract makes a play based just on possible moves given. This is called
# when the e-greedy asks for a random play to explore the curr_coords space. This can
# be pure random or informed random to try an expose more significant areas of
# curr_coords space. e.g. with some manually coded strategy for the given environment.
#


class ExplorationPlay(metaclass=abc.ABCMeta):

    #
    # Select an action from the possible actions supplied.
    #
    @abc.abstractmethod
    def select_action(self,
                      agent: Agent,
                      state: State,
                      possible_actions: [int]
                      ) -> int:
        pass
