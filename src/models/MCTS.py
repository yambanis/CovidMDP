from __future__ import division

import time
import random
from tqdm import tqdm
from joblib import Parallel, delayed
import numpy as np

def randomPolicy(state, horizon, step_size):
    for i in range(horizon):
        try:
            action = random.choice(state.getPossibleRandomActions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action, step_size)
    return state.getReward()


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
    def __init__(self,  horizon, step_size, n_jobs=6, timeLimit=None, iterationLimit=None,
                explorationConstant= 2, rolloutPolicy=randomPolicy):
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy
        self.horizon = horizon
        self.step_size = step_size
        self.n_jobs = n_jobs

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
        horizon = self.horizon
        rewards = Parallel(n_jobs=self.n_jobs)(delayed(self.rollout)(node.state, self.horizon, self.step_size)\
                                     for i in range(self.n_jobs))
        reward = np.mean(rewards)
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
                newNode = treeNode(node.state.takeAction(action, self.step_size), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        raise Exception("Should never reach here")

    def backpropogate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue =  child.totalReward / child.numVisits + (
                explorationValue * np.sqrt(np.log(node.numVisits) / child.numVisits))
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)

    def getAction(self, root):
        best_action = max(root.children, key=lambda key: root.children[key].numVisits)
        best_node = root.children[best_action]
        return best_action, best_node