### Standard Libs ###
from collections import defaultdict
from numpy.random import default_rng
import numpy as np
import networkx as nx
from itertools import chain
from tqdm import tqdm

### External Definitions ###
from zone_references import initial_districts
from disease_states import states_dict
from patient_evolution import susceptible_to_exposed, change_state
from actions import city_restrictions

def make_adjacency_list(G):
    unique_types = np.unique([data['edge_type'] for x,y, data in G.edges(data=True)])

    edge_list = {
        edge_type: np.array([(u,v) for u,v,e in G.edges(data=True) 
                                if e['edge_type'] == edge_type])
                                for edge_type in unique_types
    }
    return edge_list


def make_graph_structures(gpickle_path):
    G = nx.read_gpickle(gpickle_path)
    edge_list = make_adjacency_list(G)
    
    return G, edge_list

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

    G, edge_list = make_graph_structures(gpickle_path)

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

    matrix_change = np.apply_along_axis(susceptible_to_exposed,
                                        1, matrix_change, day=0)

    new_matrix = np.concatenate((matrix_keep, matrix_change))
    assert new_matrix.shape == pop_matrix.shape

    if return_contacts_infected:
        return new_matrix, edge_list, contacts_infected

    else:
        return new_matrix, edge_list
    
    
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
    matrix_change = pop_matrix[np.isin(pop_matrix[:, 0], exposed)]
    matrix_keep = pop_matrix[~np.isin(pop_matrix[:, 0], exposed)]
    matrix_change = np.apply_along_axis(susceptible_to_exposed,
                                        1, matrix_change, day=day)

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

    if matrix_change.shape[0] > 0:
        matrix_change = np.apply_along_axis(change_state, 1, matrix_change)

    new_matrix = np.concatenate((matrix_keep, matrix_change, matrix_no_change))

    if new_matrix.shape != pop_matrix.shape:
        raise ValueError("Input and output matrix shapes are different")
    return new_matrix

def spread_infection(pop_matrix, edge_list, restrictions, day, rng, p_r, contacts_infected=None):
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

    mask = pop_matrix[:, 1] == states_dict['infected']
    currently_infected = pop_matrix[mask][:, 0]

    if currently_infected.shape[0] == 0:
        if contacts_infected is not None:
            return pop_matrix, contacts_infected
        else:
            return pop_matrix
    
    exposed = []

    def filter_contacts(rel, prob, restrictions, currently_infected, edge_list):
        ed = edge_list[rel]
        contacts = ed[np.isin(ed[:,0], currently_infected)][:, 1]
        mask = rng.random(size=len(contacts)) < prob * (1-restrictions[rel])

        return contacts[mask]

    args = [restrictions, currently_infected, edge_list]
    exposed = list(map(lambda x: filter_contacts(x[0], x[1], *args),
                       [x for x in p_r.items()]))
    exposed = np.unique(np.concatenate(exposed)) 
    
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
    pop_matrix, edge_list = init_infection(gpickle_path)
    data = []
    total_steps = int(np.ceil(days/step_size))
    
    if isinstance(policy, str):
        policy = total_steps * [policy]
        
    if len(policy) < total_steps:
        raise ValueError(f'len of policy should be at least {total_steps}')
    
    for day in tqdm(range(1, days+1), disable=disable_tqdm):
        # if less than 90% already recovered, break simulation
        if (pop_matrix[pop_matrix[:, 1] == -1].shape[0] > pop_matrix.shape[0]*.9):
            break
            
        if day % step_size == 1:          
            current_step = int(day/step_size)
            restrictions = city_restrictions[policy[current_step]]

        pop_matrix = spread_infection(pop_matrix, edge_list, restrictions, day, rng, p_r)
        pop_matrix = lambda_leak_expose(pop_matrix, day)
        pop_matrix = update_population(pop_matrix)

        data.append(pop_matrix[:, 0:2])

    return data, pop_matrix