import simulate_pandemic as simp
from actions import costs, city_restrictions
from MCFS import mcts, treeNode
from CMDP import CovidState

from tqdm import tqdm
import numpy as np
import pickle as pkl
import datetime
from numpy.random import default_rng


import plotly.graph_objects as go
import pandas as pd

def run_full_mcts(gpickle_path, p_r, rolloutPolicy='rolloutPolicy', horizon=1, bruteForce=False,
                  sims_per_leaf=10, n_jobs=-1, step_size=7, days=210, seed=None):

    rng = default_rng(seed)
    pop_matrix, edge_list = simp.init_infection(gpickle_path)
    data = []
    actions = []


    for day in tqdm(range(1, days+1)):
        #if less than 20% still susceptible, break simulation
        if pop_matrix[np.where(pop_matrix[:,1] == -1)].shape[0] > pop_matrix.shape[0]*.9: break            
            
        
        # Choose a new policy at each week
        if day % step_size == 1:                    
            tree = mcts(sims_per_leaf=sims_per_leaf,
                        step_size=step_size,
                        horizon=horizon,
                        n_jobs=n_jobs,
                        rolloutPolicy=rolloutPolicy,
                        pop_matrix=pop_matrix,
                        rng=rng, 
                        p_r = p_r,
                        edge_list=edge_list,
                        bruteForce=bruteForce)

            root = treeNode(CovidState(actions=[], day=day), parent=None)
            action, best_node = tree.search(root)

            actions.append(action)
            restrictions = city_restrictions[action]

        pop_matrix = simp.spread_infection(pop_matrix, edge_list, 
                                           restrictions, day, rng, p_r)
        pop_matrix = simp.lambda_leak_expose(pop_matrix, day)
        pop_matrix = simp.update_population(pop_matrix)

        data.append(pop_matrix[:, 0:2])
    
    return data, actions, tree


def main():  
    prhome = 0.06
    p_r = {
        'home'    :  prhome,
        'neighbor':  .1*prhome,
        'work'    :  .1*prhome,
        'school'  :  .15*prhome,
    }

    g_pickle = '../../data/processed/SP_multiGraph_Job_Edu_Level.gpickle'

    horizon = 4
    sims = 48
    days = 364
    bf = False

    for _ in range(1):
        data, actions, tree = run_full_mcts(
                                            gpickle_path=g_pickle,
                                            p_r=p_r, 
                                            horizon=horizon,
                                            sims_per_leaf=sims,
                                            days=days,
                                            step_size=7,
                                            n_jobs=-1,
                                            bruteForce=bf
                                            )

        date = datetime.datetime.now()
        date_str = f'{date.month}_{date.day}_{date.hour}_{date.minute}'

        dfs = [pd.DataFrame(d, columns=['node_id', 'state']) for d in data]
        states_counts = [df['state'].value_counts() for df in dfs]
        ts = pd.DataFrame(states_counts).reset_index(drop=True).fillna(0)
        ts = ts.rename(columns={-1: 'removed', 
                                0: 'susceptible',
                                1: 'exposed',
                                2: 'infected',
                                3: 'hospitalized'})

        with open(f'../../data/MCTS_Results/pickles/looser_cost_H{horizon}_N{sims}_D{days}_bf{bf}_{date_str}', 'wb') as f:
            pkl.dump((data, ts, actions, tree), f)

        del data, actions, tree, ts, dfs, states_counts

if __name__ == '__main__':
    main()