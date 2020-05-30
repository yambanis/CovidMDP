import sys
sys.path.append('..')

from copy import deepcopy
from policies import policies_restrictions_by_value as possible_policies
import simulate_pandemic as simp
import numpy as np
import pandas as pd

class CovidState():
    def __init__(self, pop_matrix, day, step_size):
        self.pop_matrix = deepcopy(pop_matrix)
        self.day = day
        self.days_over_capacity = 0
        self.policy = possible_policies[0]
        self.cost_of_policies = 0
        self.current_policy = 0
        self.step_size = step_size
        self.rsieh = tuple(pd.Series(self.pop_matrix[:,1]).value_counts().sort_index())


    def getPossibleActions(self):
        possible_actions = [k for k in possible_policies.keys()]
        return possible_actions

    def getPossibleRandomActions(self):
        #possible_actions = [k for k in possible_policies.keys() 
        #                        if k >= self.current_policy]
        return self.getPossibleActions()  

    def takeAction(self, action, step_size):
        new_state = deepcopy(self)
        new_state.cost_of_policies += action
        new_state.policy = possible_policies[action]
        new_state.current_policy = action

        #spread disease for 7 days with policy
        for i in range(step_size):
            new_state.day += 1
            new_state.pop_matrix = simp.update_population(self.pop_matrix)     

            new_state.pop_matrix = simp.spread_infection(new_state.pop_matrix, new_state.policy, new_state.day)
            new_state.pop_matrix = simp.lambda_leak_expose(new_state.pop_matrix, new_state.day)

            n_hospitalized = np.where(new_state.pop_matrix[:,1] == 3)[0].shape[0]
            pop = new_state.pop_matrix.shape[0]
            if n_hospitalized/pop > 0.0025:
               # print(f'exceeded limit at day {self.day} with {n_hospitalized} hospitalized')
                new_state.days_over_capacity +=1
                                
        return new_state

    def isTerminal(self):
        return np.where(self.pop_matrix[:,1] == -1)[0].shape[0] >  self.pop_matrix.shape[0]*.9

    def getReward(self):
        return -self.cost_of_policies - 10e6 * self.days_over_capacity

    def __eq__(self, other):
        # Dois estados sao iguais se as proporcoes sao iguais no agregado da pop toda
        return self.rsieh == other.rsieh
    def __hash__(self):
        #hash da tupla representado os counts de estados na população
        return hash(self.rsieh)




class ActionInterface():
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError()