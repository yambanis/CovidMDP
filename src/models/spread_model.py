import numpy as np
import networkx as nx
import pandas as pd
import collections
from tqdm import tqdm
from joblib import Parallel, delayed

from patient_evolution import susceptible_to_exposed, infect_node, update_graph

# Start with pct% of population infected
def init_graph(initial_infection = .05, graph_model = 'relaxed_caveman',
               pop_size = 1000, seed = None):
    if graph_model == 'relaxed_caveman':
        G = nx.relaxed_caveman_graph(int(pop_size/4), 5, 0.4, seed)
    elif graph_model == 'scale_free':
        G = nx.scale_free_graph(pop_size, seed=seed)
    elif graph_model == 'SP':
        G = nx.read_gpickle('graph_SP_05_20.gpickle')
    else:
        raise ValueError("Unknown graph type")
    
    init_infection(G, initial_infection)

    return G

def init_parameters(initial_infection, graph_model, pop_size = 1000, seed=None):
    G = init_graph(initial_infection, graph_model, pop_size, seed)
    
    status = current_status(G)
    
    pop = len(G.nodes)
    i = status['infected'] / pop
    s = (pop - i) / pop
    newly_infected = status['infected']
    r, contacts_infected = 0, 0

    data = [[s,i, r, newly_infected, contacts_infected]]

    return G, data, status, pop

def init_infection(G, pct):
    """
    Given a Graph G, infects pct% of population and set the remainder as susceptible.
    This is considered day 0.
    """   
    for node in G.nodes():
        G.nodes[node].update({
                      'status': 'susceptible', 
                      'infection_day' : -1, 
                      'contacts_infected' : 0
        })

    size = int(len(G.nodes) * pct) 
    infected = np.random.choice(G.nodes, size = size, replace = False)
    
    for i in infected:
        susceptible_to_exposed(G.nodes[i], 0)

def lambda_leak_value(infected_ratio, max_value=0.05, exp=3): 
    return (infected_ratio**exp)*max_value

def current_status(G):
    """
    Returns a dict containing the current status of susceptible, infected and removed
    """
    nodes = np.array(G.nodes(data=True))[:,1]
    result = collections.Counter(node['status'] for node in nodes)
    return result

def current_status_by_zone(G):   
    result = collections.Counter(node['home'] for i,node in G.nodes(data=True) \
                                            if node['status']=='infected')

    people_per_zone = dict(collections.Counter(node['home'] for i,node in G.nodes(data=True)))
    
    for k,v in result.items():
        result[k] = v/people_per_zone[k]
        
    return dict(result)


def get_mean_contacts_infected(G):
        contacts_infected = [node['contacts_infected'] for i, node in G.nodes(data=True)\
                                                             if node['status'] == 'removed']
        if len(contacts_infected) > 0: 
            contacts_infected = np.mean(contacts_infected)
        else:
            contacts_infected = np.nan
            
        return contacts_infected
    
def get_time_series_row(G, pop):
    status = current_status(G)
    s = status['susceptible'] / pop
    i = status['infected'] / pop
    r = status['removed'] / pop
    h = status['hospitalized'] / pop
    e = status['exposed'] / pop

    contacts_infected = get_mean_contacts_infected(G)
    
    return s, e, i, r, h, contacts_infected, status

def node_contacts(G, node, p_r, restrictions, lambda_leak):
    if G.nodes[node]['status'] == 'susceptible':
        if np.random.random() < lambda_leak:
            return node, np.nan
        for node, contact, data in G.edges(node, data=True):
            if G.nodes[contact]['status'] == 'infected': 
                relation = data['edge_type']
                if np.random.random() < p_r[relation] * (1 - restrictions[relation]):
                    return node, contact
    return None, None
    
def spread_through_contacts(G, p_r, restrictions, lambda_leak):
    results = [node_contacts(G, node, p_r, restrictions, lambda_leak) for node in G.nodes()]
    results = np.array(results)
    results =  results[results[:,0] != np.array(None)]
    exposed, contacts_responsible = results[:,0], results[:,1]
    
    return exposed, contacts_responsible

def expose_contacts(G, exposed, day):
    for node in exposed:
        infect_node(G.nodes[node], day)

def increment_contacts_infected(G, contacts_responsible):
    series = pd.Series(contacts_responsible).dropna().value_counts()
    for index, value in series.items():
        G.nodes[index]['contacts_infected'] += value
        
        
def spread_one_step(G, p_r, restrictions, lambda_leak, day):
    exposed, contacts_responsible = spread_through_contacts(G, p_r, restrictions, lambda_leak)
    
    if len(exposed) > 0: 
        expose_contacts(G, exposed, day)
    if len(contacts_responsible) > 0: 
        increment_contacts_infected(G, contacts_responsible)
    
    return len(exposed)

def simulate_pandemic(restrictions={'work':0, 'school': 0, 'home':0},
                                  initial_infection=.05, 
                                  p_r={'work':.3, 'school':.5, 'home':.7},
                                  lambda_leak=0,
                                  graph_model = 'SP', pop_size = None,
                                  seed = None, it=None, policy=False):
    """
    Runs the course of the pandemic from the start until
    less than 1% of the population is simultaneously infected or no one is infected
    """
    np.random.seed(seed)
    
    G, data, status, pop = init_parameters(initial_infection, graph_model, pop_size, seed)
    
    data_per_region = []
       
    zones = range(1, 343)
    
    policy_chosen = []
    
    infected_per_relation = {
        'home': 0,
        'work' : 0,
        'school': 0
    }
    
    for day in tqdm(range(500)):
        
        if (status['removed']+status['susceptible'])>=pop:
            break
            
        update_graph(G)
       
        s, e, i, r, h, contacts_infected, status = get_time_series_row(G, pop)

        data.append([s, e, i, r, h, contacts_infected])
        
        
        if graph_model == 'SP':
            
            data_per_region.append(current_status_by_zone(G))
            
            #Lockdown
            if policy:
                if h > 0.00125: restrictions['work'], restrictions['school'] = 1, 1
                else: restrictions['work'], restrictions['school'] = 0, 0
            
            policy_chosen.append(list(restrictions.values()))
            
            newly_infected = spread_one_step(G, p_r, restrictions, lambda_leak, day)
        
            data[-1].append(newly_infected)
        
    columns = ['susceptible', 'exposed', 'infected', 'removed', 'hospitalized', 
               'contacts_infected_mean', 'newly_infected']

    time_series = pd.DataFrame(data, columns=columns)
    
    return time_series, G, data_per_region, infected_per_relation, policy_chosen

def run_simulations(number_of_rounds):
    sims = Parallel(n_jobs=-1)(delayed(simulate_pandemic)\
                       (initial_infection = .0001) for i in tqdm(range(number_of_rounds)))
    return sims