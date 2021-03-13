from joblib import Parallel, delayed
from joblib import dump, load
import os
import numpy as np
from CMDP import CovidState
from collections import defaultdict
from tqdm import tqdm
import time
import shutil

from datetime import datetime

def rolloutPolicy(state, pop_matrix, edge_list, rng, p_r, step_size):
    reward = state.takeAction(pop_matrix, edge_list, rng, p_r, step_size)
    return reward


def getRolloutPolicy(policy_name='rolloutPolicy'):
    if policy_name == 'rolloutPolicy':
        return rolloutPolicy
    raise ValueError('Unknown Rollout Policy')


class treeNode():
    def __init__(self, state, parent):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.totalReward = 0
        self.children = {}


class mcts():
    def __init__(self,
                 pop_matrix,
                 edge_list,
                 horizon, 
                 sims_per_leaf,
                 step_size,
                 rng, 
                 p_r,
                 n_jobs=6,
                 rolloutPolicy='rolloutPolicy',
                 bruteForce=True):
        self.rollout = getRolloutPolicy(rolloutPolicy)
        self.sims_per_leaf = sims_per_leaf
        self.step_size = step_size
        self.n_jobs = n_jobs
        self.pop_matrix = pop_matrix
        self.edge_list = edge_list
        self.leafs = defaultdict(list)
        self.horizon = horizon
        self.bruteForce = bruteForce
        self.rng = rng
        self.p_r = p_r

    def completed(self):
        all_levels_created = all([len(self.leafs[level]) > 0 for level in range(self.horizon)])

        fully_expanded = all([l.isFullyExpanded for level in range(self.horizon) 
                                            for l in self.leafs[level]])

        
        return all_levels_created and fully_expanded 
    
    def search(self, current_state):
        self.root = current_state
        self.leafs[0].append(self.root)
        self.expand_tree()
        assert self.completed()
        return self.getAction(self.root)

    def expand_tree(self):
        for level in range(self.horizon):
            for node in  self.leafs[level]:       
                actions = node.state.getPossibleActions(self.bruteForce)
                for action in actions:
                    new_actions = node.state.actions + [action]
                    new_state = CovidState(new_actions, node.state.day)
                    newNode = treeNode(new_state, node)
                    node.children[action] = newNode
                node.isFullyExpanded = True
                self.leafs[level+1].extend(list(node.children.values()))


    def getAction(self, root):
        leafs = self.leafs[self.horizon]
        
        """        folder = './joblib_memmap'
                try:
                    os.mkdir(folder)
                except FileExistsError:
                    pass

                edgelist_filename_memmap = os.path.join(folder, 'edgelist')
                dump(self.edge_list, edgelist_filename_memmap)
                ed_memmap = load(edgelist_filename_memmap, mmap_mode='r')

                pop_filename_memmap = os.path.join(folder, 'pop_matrix')
                dump(self.pop_matrix, pop_filename_memmap)
                pop_memmap = load(pop_filename_memmap, mmap_mode='r')
        """

        def get_total_leaf_reward(leaf_state):
            default_args = [self.pop_matrix, self.edge_list, self.rng, self.p_r, self.step_size]
            args = [leaf_state] + default_args
            rewards = list(map(lambda x: self.rollout(*args), range(self.sims_per_leaf)))
            #rewards = Parallel(n_jobs=self.n_jobs)(delayed(self.rollout)(*args)
            #                                       for i in range(self.sims_per_leaf))
            reward = np.sum(rewards)
            return reward

        rewards = Parallel(n_jobs=self.n_jobs)(delayed(get_total_leaf_reward)
                                               (leaf.state) for leaf in tqdm(leafs))

        #rewards = [get_total_leaf_reward(leaf.state) for leaf in tqdm(leafs)]
        
        
        for r,l in zip(rewards, leafs):
            l.totalReward = r
        
        """
        for leaf in leafs:
            now = datetime.now()
            args = [leaf.state,
            #rewards = list(map(lambda x: self.rollout(*args), range(self.sims_per_leaf)))
            rewards = Parallel(n_jobs=self.n_jobs)(delayed(self.rollout)
                              (*args)
                              for i in range(self.sims_per_leaf))
            later = datetime.now()
            print((later - now).total_seconds())
            reward = np.sum(rewards)
            leaf.totalReward = reward
        """

        best_node = max(leafs, key=lambda x: x.totalReward)
        best_action = best_node.state.actions[0]


        try:
            shutil.rmtree(folder)
        except:  # noqa
            print('Could not clean-up automatically.')

        return best_action, best_node
