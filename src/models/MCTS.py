import time
import random
from joblib import Parallel, delayed
import numpy as np
from CMDP import CovidState

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
        self.children = {}


class mcts():
    def __init__(self, pop_matrix, 
                 sim_rounds, step_size, n_jobs=6,
                 timeLimit=None, iterationLimit=None,
                 explorationConstant=2, 
                 rolloutPolicy='rolloutPolicy'):
        self.explorationConstant = explorationConstant
        self.rollout = getRolloutPolicy(rolloutPolicy)
        self.sim_rounds = sim_rounds
        self.step_size = step_size
        self.n_jobs = n_jobs
        self.pop_matrix = pop_matrix

        if timeLimit is not None:
            if iterationLimit is not None:
                raise ValueError("Cannot have both time and iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit is None:
                raise ValueError("Must have either time or iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'


    def search(self, current_state):
        self.root = current_state

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRound()

        return self.getAction(self.root)

    def executeRound(self):
        node = self.selectNode(self.root)
        rewards = Parallel(n_jobs=self.n_jobs)(delayed(self.rollout)
                                              (node.state, self.pop_matrix, self.step_size)
                                              for i in range(self.sim_rounds))
        reward = np.sum(rewards)
        self.backpropogate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.getPossibleActions()
        for action in actions:
            if action not in node.children:
                new_actions = node.state.actions + [action]
                new_state = CovidState(new_actions, node.state.day)
                newNode = treeNode(new_state, node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        raise Exception("Should never reach here")

    def backpropogate(self, node, reward):
        while node != self.root.parent:
            node.numVisits += self.sim_rounds
            node.totalReward += reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = child.totalReward / child.numVisits + (
                explorationValue * np.sqrt(np.log(node.numVisits)
                                           / child.numVisits))
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)

    def getAction(self, root):
        c = root.children
        best_action = max(c, key=lambda key: c[key].numVisits)
                          #key=lambda key: c[key].totalReward/c[key].numVisits)
        best_node = root.children[best_action]
        return best_action, best_node
