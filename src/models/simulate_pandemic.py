import numpy as np
import networkx as nx
from tqdm import tqdm
from disease_states import states_dict
from patient_evolution import susceptible_to_exposed, change_state
from functools import partial
from policies import policies

print('Loading Graph... ',  end='')
G = nx.read_gpickle('../../data/processed/SP_multiGraph_intID.gpickle')
print('Done!')

p_r = {
    'neighbor':  .0025,
    'work'    :  .005,
    'school'  :  .01,
    'home'    :  .8
}

def init_infection(pct=.0001):
    """
    Given a Graph G, infects pct% of population and set the
    remainder as susceptible. This is considered day 0.

    Args:
        pct (float): percentage of people initially infected.

    Returns:
        new_matrix (np.array): 2D Array  arrays of id, state, day of infection
            and current state duration of population.
    """

    global G

    size = int(len(G.nodes) * pct)
    infected = list(np.random.choice(G.nodes(), size=size, replace=False))
    infected = [x for x in infected]

    pop_matrix = np.array([[node, states_dict['susceptible'],
                            -1, -1, data['age']]
                          for node, data in G.nodes(data=True)])

    matrix_change = pop_matrix[np.isin(pop_matrix[:, 0], infected)]

    matrix_keep = pop_matrix[~np.isin(pop_matrix[:, 0], infected)]

    matrix_change = np.apply_along_axis(susceptible_to_exposed,
                                        1, matrix_change, day=0)

    new_matrix = np.concatenate((matrix_keep, matrix_change))
    assert new_matrix.shape == pop_matrix.shape

    return new_matrix


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


def lambda_leak_expose(pop_matrix, day, lambda_leak=.0001):
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

    susceptible = pop_matrix[np.where(pop_matrix[:, 1]
                                      == states_dict['susceptible'])][:, 0]

    exposed = np.random.choice(susceptible, size=size, replace=False)

    if len(exposed) == 0:
        return pop_matrix

    new_matrix = expose_population(pop_matrix, exposed, day)

    if new_matrix.shape != pop_matrix.shape:
        raise ValueError("Input and output matrix shapes are different")

    return new_matrix


def spread_through_contacts(spreader, restrictions):
    """
    An infected person, or a spredear, infects each of
    its contacts with chance equal to
    np.random.random() < p_r[r] * (1 - restrictions[r]).
    Returns an array of all the people successfully infected by the spreader.

    Args:
        spreader (int): id of the infected person that is
                        spreading the disease.

        restrictions (dictionary): a dictionary with a value between
                                   zero and one for each type of relation

    Returns:
        infected (list): List of all the people infected by spreader.
    """
    global G, p_r
    spreader = spreader
    contacts = [[y, v['edge_type']] for x, y, v
                in G.edges(spreader, data=True)]

    infected = [y for r in restrictions.keys() for y, v in contacts
                if v == r
                and np.random.random() < p_r[r] * (1 - restrictions[r])]

    return infected


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


def spread_infection(pop_matrix, restrictions, day):
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
    global G
    mask = np.where(pop_matrix[:, 1] == states_dict['infected'])
    currently_infected = pop_matrix[mask][:, 0]

    if currently_infected.shape[0] == 0:
        return pop_matrix
    exposed = list(map(partial(spread_through_contacts,
                               restrictions=restrictions),
                       currently_infected))
    exposed = np.unique(np.array([x for l in exposed for x in l]))

    mask = np.isin(pop_matrix[:, 0], exposed)
    susceptible = np.isin(pop_matrix[np.array(mask)][:, 1],
                          states_dict['susceptible'])
    exposed = pop_matrix[np.array(mask)][:, 0][susceptible]

    if len(exposed) == 0:
        return pop_matrix

    new_matrix = expose_population(pop_matrix, exposed, day)

    if new_matrix.shape != pop_matrix.shape:
        raise ValueError("Input and output matrix shapes are different")

    return new_matrix


def main(policy='unrestricted', days=500):
    pop_matrix = init_infection(.0001)

    data = []

    # restrictions={'work':0, 'school': 0, 'home':0, 'neighbor':0}
    restrictions = policies[policy]
    print(restrictions)

    for day in tqdm(range(1, days)):
        pop_matrix = update_population(pop_matrix)
        # if less than 90% already recovered, break simulation
        if (pop_matrix[np.where(pop_matrix[:, 1] == -1)].shape[0]
                > pop_matrix.shape[0]*.9):
            break

        pop_matrix = spread_infection(pop_matrix, restrictions, day)
        pop_matrix = lambda_leak_expose(pop_matrix, day)
        data.append(np.array(sorted(pop_matrix, key=lambda x: x[0]))[:, 1])

    return data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Run pandemic simulation for a given policy')
    parser.add_argument('policy', metavar='P',
                        type=str, help='the policy to be used')

    args = parser.parse_args()
    main(args.policy)
