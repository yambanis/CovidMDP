from joblib import Parallel, delayed
import numpy as np
from CMDP import CovidState
from collections import defaultdict

def rolloutPolicy(state, pop_matrix, adj_list, rng, p_r, step_size, i):
    print(f"getting rewards {i}")
    reward = state.takeAction(pop_matrix, adj_list, rng, p_r, step_size)
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
                 adj_list,
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
        self.adj_list = adj_list
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
        for leaf in leafs:
            print("Entering parallelized rewards")
            print(self.n_jobs)
            rewards = Parallel(n_jobs=self.n_jobs)(delayed(self.rollout)
                              (leaf.state, self.pop_matrix, self.adj_list, self.rng, self.p_r, self.step_size, i)
                              for i in range(self.sims_per_leaf))
            reward = np.sum(rewards)
            leaf.totalReward = reward

        best_node = max(leafs, key=lambda x: x.totalReward)
        best_action = best_node.state.actions[0]

        return best_action, best_node