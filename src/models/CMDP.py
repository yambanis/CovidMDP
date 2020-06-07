from copy import deepcopy
from policies import policies, get_policy_cost
import simulate_pandemic as simp
import numpy as np
import pandas as pd


class CovidState():
    def __init__(self, pop_matrix, day, step_size):
        self.pop_matrix = deepcopy(pop_matrix)
        self.day = day
        self.days_over_capacity = 0
        self.cost_of_policy = 0
        self.policy = None
        self.step_size = step_size
        # Recovered, Susceptible, Infected, Exposed, Hospitalized Tuple
        status = pd.Series(self.pop_matrix[:, 1])
        self.rsieh = tuple(status.value_counts().sort_index())

    def getPossibleActions(self):
        possible_actions = [k for k in policies.keys()]
        return possible_actions

    def getPossibleRangeActions(self):
        possible_actions = [(k, get_policy_cost(k)) for k in policies.keys()]
        possible_actions = sorted(possible_actions, key = lambda x: x[1])
        idx = possible_actions.index((self.policy, self.cost_of_policy))
        idx_floor = idx - 2 if idx >= 2 else 0
        idx_ceil = idx + 3 if idx <= len(possible_actions) - 3 \
                           else len(possible_actions)

        return [k for k, v in possible_actions[idx_floor:idx_ceil]] 

    def takeAction(self, action, step_size):
        # new_state = deepcopy(self)
        new_state = CovidState(self.pop_matrix, self.day, self.step_size)
        new_state.policy = action
        new_state.cost_of_policy = get_policy_cost(action)

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
            n_hospitalized = np.where(new_state.pop_matrix[:, 1] == 3)[0].shape[0]
            pop = new_state.pop_matrix.shape[0]
            if n_hospitalized/pop > 0.0025:
                new_state.days_over_capacity += 1

        # Update Recovered, Susceptible, Infected, Exposed, Hospitalized Tuple
        status = pd.Series(self.pop_matrix[:, 1])
        new_state.rsieh = tuple(status.value_counts().sort_index())
        return new_state

    def isTerminal(self):
        return (np.where(self.pop_matrix[:, 1] == -1)[0].shape[0]
                > self.pop_matrix.shape[0]*.9)

    def getReward(self):
        return (-np.sum(np.exp(self.cost_of_policy))
                - 10e6 * self.days_over_capacity)

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
