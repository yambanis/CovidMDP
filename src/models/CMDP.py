from copy import deepcopy
from policies import policies, costs
import simulate_pandemic as simp
import numpy as np
import pandas as pd
from scipy.special import expit

def normallize_to_range(x, x_min = 0.0025, x_max = 0.00275, a=-4, b=4):
    x = (x - x_min)/(x_max - x_min)
    x = (x*(b-a)) + a
    return x


def hospitalized_cost(h, capacity = 0.0025):
    return expit(normallize_to_range(h, 0, capacity))


class CovidState():
    def __init__(self, pop_matrix, day, step_size):
        self.pop_matrix = deepcopy(pop_matrix)
        self.day = day
        self.days_over_capacity = 0
        self.cost_of_policy = 0
        self.cost_hospitalized = 0
        self.policy = None
        self.step_size = step_size
        # Recovered, Susceptible, Infected, Exposed, Hospitalized Tuple
        status = pd.Series(self.pop_matrix[:, 1])
        self.rsieh = tuple(status.value_counts().sort_index())

    def getPossibleActions(self):
        possible_actions = [k for k in policies.keys()]
        return possible_actions

    def getPossibleRangeActions(self):
        # Not implemented
        possible_actions = [k for k in policies.keys()]
        return possible_actions

    def takeAction(self, action, step_size):
        new_state = CovidState(self.pop_matrix, self.day, self.step_size)
        new_state.cost_of_policy = costs[action]
        new_state.policy = action

        # spread disease for 7 days with policy
        for i in range(step_size):
            # Simulate one day
            new_state.day += 1
            new_state.pop_matrix = simp.update_population(new_state.pop_matrix)
            new_state.pop_matrix = simp.spread_infection(new_state.pop_matrix,
                                                         policies[action],
                                                         new_state.day)
            new_state.pop_matrix = simp.lambda_leak_expose(new_state.pop_matrix,
                                                           new_state.day)

            # Check if the beds capacity was exceeded
            hospitalized = np.where(new_state.pop_matrix[:, 1] == 3)[0].shape[0]
            pop = new_state.pop_matrix.shape[0]
            h = hospitalized / pop
            self.cost_hospitalized += hospitalized_cost(h)

        # Update Recovered, Susceptible, Infected, Exposed, Hospitalized Tuple
        status = pd.Series(self.pop_matrix[:, 1])
        new_state.rsieh = tuple(status.value_counts().sort_index())
        return new_state

    def isTerminal(self):
        return (np.where(self.pop_matrix[:, 1] == -1)[0].shape[0]
                > self.pop_matrix.shape[0]*.9)

    def getReward(self):
        return -self.cost_of_policy - self.cost_hospitalized

    def __eq__(self, other):
        return self.rsieh == other.rsieh

    def __hash__(self):
        # hash da tupla representado os counts de estados na população
        return hash(self.rsieh)


class ActionInterface():
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError()
