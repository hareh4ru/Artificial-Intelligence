# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState:GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState:GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState:GameState = currentGameState.generatePacmanSuccessor(action)
        curPos = currentGameState.getPacmanPosition()
        newPos = successorGameState.getPacmanPosition()
        curFood= currentGameState.getFood()
        newFood = successorGameState.getFood()
        newGhostStates:list[Agent] = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        
        "*** YOUR CODE HERE ***"        

        # check if ghost is nearby
        in_danger = 0
        minimum = curFood.height + curFood.width +1
        for ghost in newGhostStates:
            if manhattanDistance(ghost.getPosition(), curPos) <= 4:
                in_danger = 1

            if manhattanDistance(ghost.getPosition(), newPos) < minimum:
                minimum = manhattanDistance(ghost.getPosition(), newPos)

        # if min(cur position to ghosts) is less than 4 moves
        if in_danger:
            distances = 0 
            for ghost in newGhostStates:
                distances += manhattanDistance(ghost.getPosition(), newPos)
            return distances

        # if min(new position to ghosts) is less than 4 moves
        if minimum <= 4:
            return -1
                            
        minimum = curFood.height + curFood.width +1
        minPos = (0,0)
        for y in range(curFood.height):
            for x in range(curFood.width):
                if curFood[x][y]:
                    # calculate the distance from current position to nearest food
                    if manhattanDistance((x,y), curPos) < minimum:
                        minimum = manhattanDistance((x,y), curPos)
                        minPos = (x,y)
        from game import Actions
        action = Actions._directions[action]

        for i in [0,1]:
            if minPos[i] == curPos[i]:
                if action[i]:
                    return 0
                if action[1-i] == (minPos[1-i] - curPos[1-i])/abs(minPos[1-i] - curPos[1-i]):
                    return 1
                return 0
    
        for i in [0,1]:            
            if action[i] == (minPos[i] - curPos[i])//abs(minPos[i] - curPos[i]):
                return 1
        return 0
        
        # if minimum > 4:
        #     if action.x == (curPos.x - minPos.x)//abs(curPos.x - minPos.x):
        #         return 1
        #     elif action.y == (curPos.y - minPos.y)//abs(curPos.y - minPos.y):
        #         return 1
        #     return 0            

        return score

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """
    def minimax(self, gameState:GameState,depth, agentIndex):
        # reached terminal state or depth limit
        if depth == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), []

        retList = []
        for action in gameState.getLegalActions(agentIndex):
            # last ghost: increment depth
            if agentIndex == gameState.getNumAgents() - 1:
                score, path = self.minimax(gameState.generateSuccessor(agentIndex, action), depth + 1, 0)
            else:
                score, path = self.minimax(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1)
            retList.append((score, [action]+path))

        retList = sorted(retList, key=lambda x: x[0], reverse=True)
        # for pacman, return max
        if agentIndex ==0:
            return retList[0]
        # for ghost, return min
        else:
            return retList[-1]

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.
        Here are some method calls that might be useful when implementing minimax.
        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1
        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action
        gameState.getNumAgents():
        Returns the total number of agents in the game
        gameState.isWin():
        Returns whether or not the game state is a winning state
        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        return self.minimax(gameState, 0, 0)[1][0] 

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    def alphabeta(self, gameState:GameState, depth, agentIndex, alpha, beta):
        if depth == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), []

        retList = []
        for action in gameState.getLegalActions(agentIndex):
            # last ghost: increment depth
            if agentIndex == gameState.getNumAgents() - 1:
                score, path = self.alphabeta(gameState.generateSuccessor(agentIndex, action), depth + 1, 0,alpha,beta)
            else:
                score, path = self.alphabeta(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1,alpha,beta)
            retList.append((score, [action]+path))

            if agentIndex == 0:
                # beta cutoff
                if score > beta:
                    return score, [action]+path
                # alpha update
                alpha = max(score,alpha)
            else:
                # alpah cutoff
                if score < alpha:
                    return score, [action]+path
                # beta update
                beta = min(score,beta)
        
        retList = sorted(retList, key=lambda x: x[0], reverse=True)
        # for pacman, return max
        if agentIndex ==0:
            return retList[0]
        # for ghost, return min
        else:
            return retList[-1]

 

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        return self.alphabeta(gameState, 0, 0,-0xffffffff,0xffffffff)[1][0] 


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
