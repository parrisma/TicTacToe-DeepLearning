import unittest
import logging
import random
import numpy as np
import keras
from pathlib import Path
from random import randint
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.wrappers.scikit_learn import KerasRegressor
from reflrn import Policy
from reflrn import State
from reflrn import EnvironmentLogging
from reflrn import EvaluationException
from reflrn import ReplayMemory
from reflrn import ModelParameters
import matplotlib.pyplot as plt

#
# This follows the ActorCritic pattern.
#


class TemporalDifferenceActorCriticDeepNNPolicy(Policy):

    # Learning Parameters
    __n = 0  # number of learning events
    __learning_rate_0 = float(0.05)
    __discount_factor = float(0.8)
    __learning_rate_decay = float(0.001)

    #
    # At inti time the only thing needed is the universal set of possible
    # actions for the given Environment
    #
    def __init__(self,
                 lg: logging,
                 replay_memory:
                 ReplayMemory,
                 model_file_name: str,
                 model_parameters: ModelParameters=None,
                 load_model: bool=False):

        self.__lg = lg
        if load_model:
            self.load(model_file_name)
        else:
            self.__actor = self.create_new_model_instance()
            self.__critic = self.create_new_model_instance()
        self.__episodes_played = 0
        self.__model_file_name = model_file_name
        self.__critic_updates = 0
        self.__replay_memory = replay_memory
        if model_parameters is None:
            mp = ModelParameters()  # Defaults
        else:
            mp = model_parameters

        self.__epochs = mp.epochs
        self.__update_every_n_episodes = mp.update_every_n_episodes
        self.__sample_size = mp.sample_size
        self.__batch_size = mp.batch_size
        self.__replay_mem_size = mp.replay_mem_size
        self.__save_every_n_critic_updates = mp.save_every_n_critic_updates

        return

    #
    # Define the model that will approximate the Q Value function.
    # X: 1 by 9 : State Of the Board.
    # Y: 1 by 9 : Q Values for the 9 possible actions.
    #
    @classmethod
    def create_new_model_instance(cls) -> keras.models.Sequential:

        model = Sequential()
        model.add(Dense(50, input_dim=9, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(500, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(9))
        cls.__compile_model(model)

        return model

    #
    # Compile the Keras Model
    #
    @classmethod
    def __compile_model(cls, model):
        model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
        return

    #
    # Return the learning rate based on number of learning's to date
    #
    @classmethod
    def __learning_rate(cls):
        return cls.__learning_rate_0 / (1 + (cls.__n * cls.__learning_rate_decay))

    #
    # We do not update the policy, we just train the model once at the outset via the train() method.
    # This is **not** a Critic / Actor Pattern
    #
    def update_policy(self,
                      agent_name: str,
                      state: State,
                      next_state: State,
                      action: int,
                      reward: float,
                      episode_complete: bool):

        # Record the number of learning events.
        self.__n += 1

        # Track the SAR for critic training.
        self.__replay_memory.appendMemory(state, next_state, action, reward, episode_complete)

        # Track the number of finished episodes, this drives the learning updates.
        if episode_complete:
            self.__episodes_played += 1

        # Every so often, we train the critic from memories and swap it in as the new actor.
        if self.__replay_memory.len() > self.__sample_size and (self.__episodes_played % self.__update_every_n_episodes) == 0:
            memories = self.get_random_memories()
            x, y = self.random_memories_to_training_xy(memories)
            self.train_critic_and_update_actor(x, y)

    #
    # Extract a random set of memories equal to the defined sample size.
    #
    def get_random_memories(self):
        return self.__replay_memory.getRandomMemories(self.__sample_size)

    #
    # Convert a given set of memories to x,y training inputs. As part of this we apply the temporal difference
    # updates to the q values predicted by the actor.
    #
    def random_memories_to_training_xy(self, memories):
        lnm = len(memories[0])
        x = np.empty((lnm, 9))
        y = np.empty((lnm, 9))
        for i in range(0, lnm):
            state = memories[ReplayMemory.mem_state][i]
            next_state = memories[ReplayMemory.mem_next_state][i]
            action = memories[ReplayMemory.mem_action][i]
            reward = memories[ReplayMemory.mem_reward][i]

            # Extract states as numpy arrays (in form needed for the NN as input X)

            s = self.state_as_str_to_numpy_array(state.state_as_string())
            ns = self.state_as_str_to_numpy_array(next_state.state_as_string())

            lr = self.__learning_rate()

            qvns = self.__actor.predict(np.array([ns]))[0]
            mxq = np.max(qvns)
            qvp = self.__discount_factor * mxq * lr

            qv = self.__actor.predict(np.array([s]))[0]
            qv[action] = (qv[action] * (1 - lr)) + (lr * reward) + qvp
            mn = np.min(qv)
            mx = np.max(qv)
            if mx - mn != 0:
                qv = (qv-mn) / (mx - mn)

            x[i] = s
            y[i] = qv

        return x, y

    #
    # Train the model given a set of State/Q Values saved from the TemporalDifferencePolicy Class. The model's
    # ability to predict the action will be no better then the ability of the Q Values. This is simply an exercise
    # in using a Deep NN as an interim step to understanding the full actor/critic policy.
    #
    # The given file name is the name of a Q Value dump file.
    #
    def train_critic_and_update_actor(self, x, y):

        self.__critic.fit(x, y, epochs=self.__epochs, batch_size=self.__batch_size, verbose=0)
        scores = self.__critic.evaluate(x, y)
        self.__lg.info("Critic Accuracy %s: %.2f%%" % (self.__critic.metrics_names[1], scores[1] * 100))

        self.__critic_updates += 1
        if self.__critic_updates % self.__save_every_n_critic_updates == 0:
            self.__critic.save(self.__model_file_name)
            self.__lg.info("Critic Saved")
        self.__actor = keras.models.clone_model(self.__critic)  # Make the actor = to (newly retrained) Critic
        self.__compile_model(self.__actor)
        return

    #
    # Convert a state string to numpy vector
    #
    @classmethod
    def state_as_str_to_numpy_array(cls, xs: str) -> np.array:
        xl = list()
        s = 1
        for c in xs:
            if c == '-':
                s = -1
            else:
                xl.append(float(c) * float(s))
                s = 1
        return np.asarray(xl, dtype=np.float32)

    #
    # Greedy action; The current version of the Actor predicts the Q Values.
    #
    def greedy_action(self, agent_name: str, state: State, possible_actions: [int]) -> int:

        qvs = None
        if self.__actor is not None:
            qvs = self.__actor.predict(np.array([self.state_as_str_to_numpy_array(state.state_as_string())]))[0]
            self.__lg.debug("Predict Y:= " + str(qvs))
        else:
            raise EvaluationException("No (Keras) Model Loaded with which to predict Q Values")

        ou = np.max(qvs)
        greedy_actions = list()
        for i in range(0, len(qvs)):
            if qvs[i] == ou:
                if i in possible_actions:
                    greedy_actions.append(int(i))
        if len(greedy_actions) == 0:
            raise EvaluationException("Model did not predict a Q Values related to a possible action")

        return greedy_actions[randint(0, len(greedy_actions)-1)]

    #
    # Save, not relevant for this Policy type
    #
    def save(self, filename: str=None):
        # Save is done as part of policy update, not on the environment call back
        return

    #
    # Load the last critic Keras Deep NN
    #
    def load(self, filename: str=None):
        if Path(filename).is_file():
            self.__actor = keras.models.load_model(filename)
            self.__critic = keras.models.clone_model(self.__actor)
            self.__compile_model(self.__critic)
            self.__lg.info("Critic & Actor Loaded from file: " + filename)
        else:
            self.__actor = self.create_new_model_instance()
            self.__critic = self.create_new_model_instance()
            self.__lg.info("Critic & Actor not loaded as file not found: " + filename)
        return

# ********************
# *** UNIT TESTING ***
# ********************


class TestTemporalDifferenceActorCriticDeepNNPolicy(unittest.TestCase):

        __qval_file = 'qvn_dump.pb'
        __model_file = 'model.keras'
        __lg = None

        @classmethod
        def setUpClass(cls):
            random.seed(42)
            np.random.seed(42)
            cls.__lg = EnvironmentLogging("TestTemporalDifferenceDeepNNPolicy",
                                          "TestTemporalDifferenceDeepNNPolicy.log",
                                          logging.INFO).get_logger()

        #
        # Test the NN model behaviour.
        #
        # Is the defined model able to learn and predict a single state action pair.
        #
        def test_model_behaviour_1(self):

            nn_model = TemporalDifferenceActorCriticDeepNNPolicy.create_new_model_instance()
            x = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
            y = np.array([1.1234, 2.1234, 3.1234, 4.1234, 5.1234, 6.1234, 7.1234, 8.1234, 9.1234])
            nt = 500
            xx = np.reshape(np.repeat(x, nt, axis=-1), (x.size, nt)).T
            yy = np.reshape(np.repeat(y, nt, axis=-1), (y.size, nt)).T

            err = 1e9
            iter = 0
            model_loss = 1e9
            model_acc = 1e9
            while (err > 1e-6 or model_loss > 1e-9) and model_acc > 0.75 and iter < 10:
                nn_model.fit(xx, yy, batch_size=35, epochs=50, shuffle=False)
                pr = nn_model.predict(np.array([x]))[0]
                err = np.max(np.absolute(y-pr))
                scores = nn_model.evaluate(xx, yy)
                model_loss = scores[0]
                model_acc = scores[1]
                iter += 1

            self.__lg.debug("Final Prediction: " + str(pr))
            self.assertGreater(1e-6, err)
            self.assertGreater(1e-6, model_loss)
            self.assertGreater(model_acc, 0.75)
            return

        #
        # Test the NN model behaviour.
        #
        # Is the defined model able to learn and predict 1000 state action pairs in a replay memory
        # of 10K samples with each pair repeated 10 times
        #
        def test_model_behaviour_1000(self):

            nn_model = TemporalDifferenceActorCriticDeepNNPolicy.create_new_model_instance()
            nt = 100
            x = np.empty((nt, 9))
            y = np.empty((nt, 9))
            for i in range(0, nt):
                xr = self.__rand_x()
                yr = self.__rand_y()
                x[i] = xr
                y[i] = yr

            err = 1e9
            iter = 0
            model_loss = 1e9
            model_acc = 0
            while err > 1e-6 and model_loss > 1e-9 and model_acc < 0.75 and iter < 1000:
                nn_model.fit(x, y, batch_size=33, epochs=5000, shuffle=False)
                pr = nn_model.predict(x)[0]
                err = np.max(np.absolute(y-pr))
                scores = nn_model.evaluate(x, y)
                model_loss = scores[0]
                model_acc = scores[1]
                iter += 1

            self.__lg.debug("Final Prediction: " + str(pr))
            self.assertGreater(1e-6, err)
            self.assertGreater(1e-6, model_loss)
            self.assertGreater(model_acc, 0.75)
            return

        #
        # Test the NN model behaviour.
        #
        # arbitrary quadratic
        #
        def test_model_behaviour_quad(self):

            model = Sequential()
            model.add(Dense(2, input_dim=2, activation='relu'))
            model.add(Dropout(0.5))
            model.add(Dense(1))
            model.compile(loss='mean_squared_error', optimizer='adam')

            nt = 200
            x = np.empty((nt, 2))
            y = np.empty((nt, 1))
            for i in range(0, nt):
                xr = np.array([i, i*i])
                yr = 2*xr[0] + xr[1] + 1
                x[i] = xr
                y[i] = yr

            plt.plot(x[:, 0], y)
            plt.show()

            estimator = KerasRegressor(build_fn=model, nb_epoch=100, batch_size=5, verbose=0)
            estimator.fit(x, y)
            pr = estimator.predict(x)
            err = np.max(np.absolute(y-pr))
            scores = model.evaluate(x, y)
            model_loss = scores[0]
            model_acc = scores[1]
            iter += 1

            self.__lg.debug("Final Prediction: " + str(pr))
            self.assertGreater(1e-6, err)
            self.assertGreater(1e-6, model_loss)
            self.assertGreater(model_acc, 0.75)
            return

        #
        # return a random x "state" vector
        #
        def __rand_x(self) -> np.array:
            x = np.random.randint(low=-1, high=1, size=(1, 9))
            x = x * np.float(1)
            return x

        #
        # return a random y "state" vector
        #
        def __rand_y(self) -> np.array:
            y = np.random.rand(1, 9)*100
            return y

        #
        # Test convergence on single game pattern.
        #
        # Game is moves 0,2,4,6,8 (diagonal win)
        #
        def test_training(self):
            ts0 = TestState("000000000")
            ts1 = TestState("100000000")
            ts2 = TestState("10-1000000")
            ts3 = TestState("10-1010000")
            ts4 = TestState("10-1010-100")
            ts5 = TestState("10-1010-101")

            test_cases = (('1', ts0, ts1, 0, 0.0, False),
                          ('-1', ts1, ts2, 2, 0.0, False),
                          ('1', ts2, ts3, 4, 0.0, False),
                          ('-1', ts3, ts4, 6, 0.0, False),
                          ('1', ts4, ts5, 8, 100.0, True),
                          )

            rpmem_sz = 500
            rm = ReplayMemory(self.__lg, rpmem_sz)
            mp = ModelParameters(10, 10, 50, 10, rpmem_sz, 25)
            tdacdnnp = TemporalDifferenceActorCriticDeepNNPolicy(self.__lg, rm, "./model.test", mp, False)

            for i in range(0, 200):
                case = test_cases[i % 5]
                tdacdnnp.update_policy(case[0], case[1], case[2], case[3], case[4], case[5])

            pa0 = tdacdnnp.greedy_action("1", ts0, [0, 1, 2, 3, 4, 5, 6, 7, 8])
            pa1 = tdacdnnp.greedy_action("1", ts1, [0, 1, 3, 4, 5, 6, 7, 8])
            pa2 = tdacdnnp.greedy_action("1", ts2, [0, 1, 3, 5, 6, 7, 8])
            pa3 = tdacdnnp.greedy_action("1", ts3, [0, 1, 3, 5, 7, 8])
            pa4 = tdacdnnp.greedy_action("1", ts4, [0, 1, 3, 5, 7])

            return

#
# Execute the tests.
#


if __name__ == "__main__":
    if False:
        tests = TestTemporalDifferenceActorCriticDeepNNPolicy()
        suite = unittest.TestLoader().loadTestsFromModule(tests)
        unittest.TextTestRunner().run(suite)
    else:
        suite = unittest.TestSuite()
        suite.addTest(TestTemporalDifferenceActorCriticDeepNNPolicy("test_model_behaviour_quad"))
        unittest.TextTestRunner().run(suite)

