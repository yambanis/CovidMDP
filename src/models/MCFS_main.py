import simulate_pandemic as simp
from actions import costs, city_restrictions
from MCFS import mcts, treeNode
from CMDP import CovidState


from tqdm import tqdm
import numpy as np
import pickle as pkl
import datetime


import plotly.graph_objects as go
import pandas as pd

def run_full_mcst(rolloutPolicy='rolloutPolicy', horizon=1, bruteForce=False,
                  sims_per_leaf=10, n_jobs = 6, step_size = 7, days = 210):

    pop_matrix = simp.init_infection()
    data = []
    actions = []

    for day in tqdm(range(1, days+1)):
        #if less than 20% still susceptible, break simulation
        if pop_matrix[np.where(pop_matrix[:,1] == -1)].shape[0] > pop_matrix.shape[0]*.9: break            
            
        
        # Choose a new policy at each week
        if day % step_size == 1:                    
            tree = mcts(sims_per_leaf=sims_per_leaf, step_size=step_size, horizon=horizon,
                        n_jobs=n_jobs, rolloutPolicy=rolloutPolicy, pop_matrix=pop_matrix, bruteForce=bruteForce)

            root = treeNode(CovidState(actions=[], day=day), parent=None)
            action, best_node = tree.search(root)

            actions.append(action)
            restrictions = city_restrictions[action]

        pop_matrix = simp.spread_infection(pop_matrix, restrictions, day)
        pop_matrix = simp.lambda_leak_expose(pop_matrix, day)
        pop_matrix = simp.update_population(pop_matrix)

        data.append(np.array(sorted(pop_matrix,key=lambda x: x[0]))[:,1]) 
    
    return data, actions, tree


def main():
	horizon = 1
	sims = 6
	days = 210
	bf = False

	data, actions, tree = run_full_mcst(horizon=horizon, sims_per_leaf=sims, days=days, step_size=7, n_jobs=6, bruteForce=bf)

	date = datetime.datetime.now()
	date_str = f'{date.month}_{date.day}_{date.hour}_{date.minute}'


	data = pd.DataFrame([pd.Series(d).value_counts() for d in data])
	data.fillna(0, inplace=True)

	with open(f'../../data/MCTS_Results/pickles/looser_cost_H{horizon}_N{sims}_D{days}_bf{bf}_{date_str}', 'wb') as f:
	    pkl.dump((data, actions, tree), f)

if __name__ == '__main__':
	main()