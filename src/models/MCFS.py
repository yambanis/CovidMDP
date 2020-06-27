from joblib import Parallel, delayed
import numpy as np
from CMDP import CovidState
from collections import defaultdict

def rolloutPolicy(state, pop_matrix, step_size):
    reward = state.takeAction(pop_matrix, step_size)
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
        self.numVisits = 0
        self.totalReward = 0
        self.bestReward = float("-inf")
        self.children = {}


class mcts():
    def __init__(self, pop_matrix, horizon, 
                 sims_per_leaf, step_size, n_jobs=6,
                 rolloutPolicy='rolloutPolicy'):
        self.rollout = getRolloutPolicy(rolloutPolicy)
        self.sims_per_leaf = sims_per_leaf
        self.step_size = step_size
        self.n_jobs = n_jobs
        self.pop_matrix = pop_matrix
        self.leafs = defaultdict(list)
        self.horizon = horizon
        self.searchLimit = np.sum([5**i for i in range(horizon)])


    def search(self, current_state):
        self.root = current_state
        for i in range(self.searchLimit):
            self.executeRound()
        return self.getAction(self.root)

    def executeRound(self):
        nodes, level = self.selectNode(self.root)
        self.leafs[level].extend(list(nodes.values()))
        for node in nodes.values():
            self.backpropogate(node)

    def selectNode(self, node):
        level = 1
        while not node.isTerminal:
            if node.isFullyExpanded:
                level += 1
                node = self.getBestChild(node)
            else:
                return self.expand(node, level)

        raise Exception("Should never reach here")


    def getBestChild(self, node):
        c = node.children
        least_seen = min(c, key=lambda key: c[key].numVisits)
        return node.children[least_seen]


    def expand(self, node, level):
        actions = node.state.getPossibleActions()
        for action in actions:
            new_actions = node.state.actions + [action]
            new_state = CovidState(new_actions, node.state.day)
            newNode = treeNode(new_state, node)
            node.children[action] = newNode
        node.isFullyExpanded = True
        return node.children, level

        raise Exception("Should never reach here")

    def backpropogate(self, node):
        while node != self.root.parent:
            node.numVisits += 1
            node = node.parent


    def getAction(self, root):
        leafs = self.leafs[self.horizon]
        for leaf in leafs:
            rewards = Parallel(n_jobs=self.n_jobs)(delayed(self.rollout)
                              (leaf.state, self.pop_matrix, self.step_size)
                              for i in range(self.sims_per_leaf))
            reward = np.sum(rewards)
            leaf.totalReward = reward

        best_node = max(leafs, key=lambda x: x.totalReward)
        best_action = best_node.state.actions[0]

        return best_action, best_node