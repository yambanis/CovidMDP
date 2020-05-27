from copy import deepcopy
from spread_model import init_parameters, spread_one_step, get_time_series_row
from patient_evolution import update_graph
from collections import defaultdict

class CovidState():
    def __init__(self, file_path, graph_model = 'SP', seed = None, 
                                pop_size=None, initial_infection=0.0001,
                                p_r={'neighbor':.001,'work':.003,'school':.005,'home':.7}):
        
        self.G, self.data, self.status, self.pop = init_parameters(initial_infection,
                                                                   graph_model, file_path, 
                                                                   pop_size, seed)
        self.day = 0
        self.exceed_beds = False
        self.p_r = p_r

    def getPossibleActions(self):
        possible_actions = [
            #Lockdown
            (1, 1, 1, 3),
            #(.75, 1, .75),
            #(.5, 1, .5),
            (.25, 1, .25, 1.5),
            (.75, 0, .75, 1),
            #(.5, 0, .5),
            (.25, 0, .25, .5),
            (0, 0, 0, 0)
        ]

        return possible_actions

    def takeAction(self, action):
        new_state = deepcopy(self)
        update_graph(new_state.G)
       
        s,e,i,r,h,contacts_infected,status = get_time_series_row(new_state.G, new_state.pop)

        new_state.data.append([s, e, i, r, h, contacts_infected])

        new_state.day += 1
        print(new_state.day)

        new_state.cost_of_restrictions += action[3]

        restrictions = {'work':action[0], 'school':action[1], 
                        'neighbor':action[2], 'home':0}

        newly_infected = spread_one_step(new_state.G, new_state.p_r, restrictions,
                                                infected_per_relation=defaultdict(int), 
                                                lambda_leak=0, day=new_state.day)
        
        new_state.data[-1].append(newly_infected)

        new_state.exceed_beds =  new_state.exceed_beds or new_state.data[-1][4] > 0.0025

        return new_state



    def isTerminal(self):
        return self.status['susceptible']/self.pop < .2 or self.day > 100 or \
                        self.status['infected']/self.pop

    def getReward(self):
        return -self.cost_of_restrictions - 10e6 * self.exceed_beds

    def __eq__(self, other):
        raise NotImplementedError()
        # Dois estados sao iguais se as proporcoes sao iguais no agregado da pop toda



class ActionInterface():
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError()