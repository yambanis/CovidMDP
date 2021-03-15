### Standard Libs ###
from collections import defaultdict
from numpy.random import default_rng
import numpy as np
import networkx as nx
from tqdm import tqdm
from datetime import datetime
from disease_evolution import incubation, hospitalization_to_removed
from disease_evolution import onset_to_hosp_or_asymp, needs_hospitalization

### External Definitions ###
from zone_references import initial_districts
from disease_states import states_dict
from patient_evolution import change_state
from actions import city_restrictions

def make_adjacency_list(G):
    edge_types = np.unique([d['edge_type'] for u,v,d in G.edges(data=True)])
    adj_list = {k: defaultdict(list) for k in edge_types}
    
    for node, neighbors in G.adjacency():
        for neighbor, relations in neighbors.items():
            for _, relation_dict in relations.items():
                relation = relation_dict['edge_type']
                adj_list[relation][node].append(neighbor)
       
    return adj_list


def make_graph_structures(gpickle_path):
    G = nx.read_gpickle(gpickle_path)
    adj_list = make_adjacency_list(G)
    
    return G, adj_list

def init_infection(gpickle_path, pct=.0005, return_contacts_infected=False):
    """
    Given a Graph G, infects pct% of population and set the
    remainder as susceptible. This is considered day 0.
    Args:
        pct (float): percentage of people initially infected.
    Returns:
        new_matrix (np.array): 2D Array  arrays of id, state, day of infection
            and current state duration of population.
    """

    G, adj_list = make_graph_structures(gpickle_path)

    sample_size = int(np.ceil(len(G.nodes()) * pct/len(initial_districts)))
    size = max(sample_size, 1)

    infected = []
    for zones in initial_districts.values():
        init_nodes = ([x for x, v in G.nodes(data=True) 
                           if v['home'] in zones])

        infected.extend(list(np.random.choice(init_nodes, size=size, replace=False)))

    pop_matrix = np.array([[node, states_dict['susceptible'],
                            -1, -1, data['age']]
                          for node, data in G.nodes(data=True)]).astype(int)
    
    contacts_infected = defaultdict(int)

    matrix_change = pop_matrix[np.isin(pop_matrix[:, 0], infected)]

    matrix_keep = pop_matrix[~np.isin(pop_matrix[:, 0], infected)]

    matrix_change[:, 1] = states_dict['exposed']
    matrix_change[:, 2] = 0
    matrix_change[:, 3] = incubation(size=matrix_change.shape[0])

    new_matrix = np.concatenate((matrix_keep, matrix_change))
    assert new_matrix.shape == pop_matrix.shape

    if return_contacts_infected:
        return new_matrix, adj_list, contacts_infected

    else:
        return new_matrix, adj_list
    
    
def expose_population(pop_matrix, exposed, day):
    """
    Receives the population matrix, an array containing ids of newly
    exposed individuals and the current simulation day
    Args:
        pop_matrix (np.array): 2D Array  arrays of id, state, day of infection
            and current state duration of population.
        exposed (list): list of newly exposed people id
        day (int): current simulation day
    Returns:
        new_matrix (np.array): The population matrix with the
        newly exposed people exposed.
    Raises:
        ValueError: If shape of starting matrix is different from final matrix
    """
    st = datetime.now()
    matrix_change = pop_matrix[np.isin(pop_matrix[:, 0], exposed)]
    matrix_keep = pop_matrix[~np.isin(pop_matrix[:, 0], exposed)]

    if (matrix_change[:, 1] != states_dict['susceptible']).sum() != 0:
        raise ValueError("Node status different from susceptible")

    matrix_change[:, 1] = states_dict['exposed']
    matrix_change[:, 2] = day
    matrix_change[:, 3] = incubation(size=matrix_change.shape[0])
    new_matrix = np.concatenate((matrix_keep, matrix_change))    
    if new_matrix.shape != pop_matrix.shape:
        raise ValueError("Input and output matrix shapes are different")
    return new_matrix

def lambda_leak_expose(pop_matrix, day, lambda_leak=0.00005):
    """
    Receives the population matrix, the current day and the leak factor.
    Chooses at random a lambda_leak percentage of the population to expose
    Args:
        pop_matrix (np.array): 2D Array  arrays of id, state, day of infection
            and current state duration of population.
        lambda_leak (float): the percentage of the population to expose
        day: the current day of simulation
    Returns:
        new_matrix (np.array): The population matrix with the
                               newly exposed people.
    Raises:
        ValueError: If shape of starting matrix is different from final matrix
    """
    st = datetime.now()

    size = int(pop_matrix.shape[0]*lambda_leak)
    susceptible = pop_matrix[pop_matrix[:, 1] == states_dict['susceptible']][:, 0]

    exposed = np.random.choice(susceptible, size=size, replace=False)

    if len(exposed) == 0:    
        return pop_matrix

    new_matrix = expose_population(pop_matrix, exposed, day)

    if new_matrix.shape != pop_matrix.shape:
        raise ValueError("Input and output matrix shapes are different")    
    return new_matrix

def update_population(pop_matrix):
    """
    Receives the population matrix and progress the infections
    for all people. The state duration is decremented
    and for those whom it reaches zero, they transition to the next state
    Args:
        pop_matrix (np.array): 2D Array  arrays of id, state, day of infection
            and current state duration of population.
    Returns:
        new_matrix (np.array): The population matrix with the updated status.
    Raises:
        ValueError: If shape of starting matrix is different from final matrix
    """
    st = datetime.now()

    matrix_keep = pop_matrix[np.isin(pop_matrix[:, 1],
                                     [states_dict['susceptible'],
                                     states_dict['removed']]
                                     )]
    matrix_change = pop_matrix[~np.isin(pop_matrix[:, 1],
                                        [states_dict['susceptible'],
                                        states_dict['removed']]
                                        )]

    matrix_change[:, 3] = matrix_change[:, 3].astype(int) - 1
    matrix_no_change = matrix_change[matrix_change[:, 3].astype(int) > 0]
    matrix_change = matrix_change[matrix_change[:, 3].astype(int) == 0]

    from_exposed = matrix_change[matrix_change[:, 1] == states_dict['exposed']]
    from_exposed[:, 1] = states_dict['infected']
    from_exposed[:, 3] = onset_to_hosp_or_asymp(size=from_exposed.shape[0])

    from_infected = matrix_change[matrix_change[:, 1] == states_dict['infected']]
    
    if len(from_infected) > 0:
        becomes_hospitalized = np.array([needs_hospitalization(age) for age in from_infected[:,4]])
        to_hospitalized = from_infected[becomes_hospitalized]
        to_hospitalized[:,1] = states_dict['hospitalized']
        to_hospitalized[:, 3] = hospitalization_to_removed(size=to_hospitalized.shape[0])
        to_removed = from_infected[~becomes_hospitalized]
        to_removed[:, 1] = states_dict['removed']
        from_infected = np.concatenate([to_removed, to_hospitalized])

    from_hospitalized = matrix_change[matrix_change[:, 1] == states_dict['hospitalized']]
    from_hospitalized[:, 1] = states_dict['removed']

    new_matrix = np.concatenate([matrix_keep,
                                 matrix_no_change,
                                 from_exposed,
                                 from_infected,
                                 from_hospitalized  
                                ])    

    if new_matrix.shape != pop_matrix.shape:
        raise ValueError("Input and output matrix shapes are different")
    return new_matrix

def spread_infection(pop_matrix, adj_list, restrictions, day, rng, p_r, contacts_infected=None):
    """
    Receives the population matrix, the restrictions dictionary and the
    current day. The disease spreads throught the relations in the graph:
    each infected person has a chance to infect a susceptible contact with
    it has an edge in the graph, conditioned to the current restrictions,
    the p_r of each relation.
    Args:
        pop_matrix (np.array): 2D Array  arrays of id, state, day of infection
            and current state duration of population.
        restrictions (dictionary): a dictionary with a value between
        zero and one for each type of relation
        day: the current day of simulation
    Returns:
        new_matrix (np.array): The population matrix with the newly
                                exposed people.
    Raises:
        ValueError: If shape of starting matrix is different from final matrix
    """
    st = datetime.now()

    mask = pop_matrix[:, 1] == states_dict['infected']
    currently_infected = pop_matrix[mask][:, 0]

    if currently_infected.shape[0] == 0:    
        if contacts_infected is not None:
            return pop_matrix, contacts_infected
        else:
            return pop_matrix

    exposed = []

    for relation, prob in p_r.items():
        pairs = [contact 
                 for i in currently_infected
                 for contact in adj_list[relation][i]     
                ]
        pairs = np.array(pairs)
        chances = rng.random(size=len(pairs)) < prob * (1-restrictions[relation])

        exposed.extend(pairs[chances])
    
    exposed = np.unique(exposed).astype(int)    
        
    mask = np.isin(pop_matrix[:, 0], exposed)
    susceptible = np.isin(pop_matrix[np.array(mask)][:, 1],
                          states_dict['susceptible'])
    exposed = pop_matrix[np.array(mask)][:, 0][susceptible]

    if len(exposed) == 0:    
        if contacts_infected is not None:
            return pop_matrix, contacts_infected
        else:
            return pop_matrix
        

    new_matrix = expose_population(pop_matrix, exposed, day)

    if new_matrix.shape != pop_matrix.shape:
        raise ValueError("Input and output matrix shapes are different")    

    if contacts_infected is not None:
        return new_matrix, contacts_infected
    else:
        return new_matrix
    
def main(gpickle_path, p_r, policy='Unrestricted',
         days=350, step_size=7,
         disable_tqdm=False, seed=None):
    """
    Receives the policy to be used during the simulation and for how many days
    the simulation should run for. The policy should be a Key in the policies
    dict inside policies.py.
    One full step consists of:
        Spreading the infection
        Exposing through leakage
        Updating the disease evolution of the population
    Args:
        pop_matrix (string): The name of a policy that exists is policies.policies.
        days (int): For how long should the policy run.
    Returns: data (np.array): An array of arrays containing the status of 
    the population at each time step.
    
    """
    
    rng = default_rng(seed)
    pop_matrix, adj_list = init_infection(gpickle_path)
    data = []
    total_steps = int(np.ceil(days/step_size))
    
    if isinstance(policy, str):
        policy = total_steps * [policy]
        
    if len(policy) < total_steps:
        raise ValueError(f'len of policy should be at least {total_steps}')
    
    for day in tqdm(range(1, days), disable=disable_tqdm):
        # if less than 90% already recovered, break simulation
        if (pop_matrix[pop_matrix[:, 1] == -1].shape[0] > pop_matrix.shape[0]*.9):
            break
            
        if day % step_size == 1:          
            current_step = int(day/step_size)
            restrictions = city_restrictions[policy[current_step]]

        pop_matrix = spread_infection(pop_matrix, adj_list, restrictions, day, rng, p_r)
        pop_matrix = lambda_leak_expose(pop_matrix, day)
        pop_matrix = update_population(pop_matrix)

        data.append(pop_matrix[:, 0:2])

    return data, pop_matrix