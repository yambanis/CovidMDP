from copy import deepcopy
import simulate_pandemic as simp
import numpy as np
import random
from actions import exposed_cost, costs, city_restrictions


class CovidState():
    def __init__(self, actions, day):
        self.day = day
        self.actions = actions
        self.cost = None

    def getPossibleActions(self):
        possible_actions = [k for k in city_restrictions.keys()]
        random.shuffle(possible_actions)
        return possible_actions

    def takeAction(self, pop_matrix, step_size):
        local_pop_matrix = deepcopy(pop_matrix)
        pop = local_pop_matrix.shape[0]

        day = self.day
        sims_costs = []

        for action in self.actions:
            cost_action = costs[action]*step_size
            cost_exposed = 0
            
            # spread disease for step_size days with policy
            for i in range(step_size):
                # Simulate one day
                day += 1
                local_pop_matrix= simp.spread_infection(local_pop_matrix,
                                                            city_restrictions[action],
                                                            day)
                local_pop_matrix = simp.lambda_leak_expose(local_pop_matrix,
                                                            day)
                local_pop_matrix = simp.update_population(local_pop_matrix)
                        
                e = np.where(local_pop_matrix[:, 1] == 1)[0].shape[0] / pop
                cost_exposed += exposed_cost(e)        
            
            sims_costs.append(max(cost_action, cost_exposed))
        
        self.cost = -1*np.sum([c*0.8**i for i,c in enumerate(sims_costs)])
        
        return self.cost

    def isTerminal(self):
        return False
        #return (np.where(self.pop_matrix[:, 1] == -1)[0].shape[0] > self.pop_matrix.shape[0]*.9)

    def getReward(self):
        return self.cost
        #return min(-self.cost_of_policy, -self.cost_exposed)

    def __eq__(self, other):
        return self.actions == other.actions

    def __hash__(self):
        # hash da tupla representado os counts de estados na população
        return hash(self.rsieh)


class ActionInterface():
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError()
