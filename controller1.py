import numpy as np
from random import randint
from global_vars import *

class Controller:
	valFunc = [];
	transitionMatrix = []
	rewardMatrix = []
	probabilityMatrix = []
	gamma = 0
	prevState = DEATH_STATE
	prevAction = 1
	
	def __init__(self, gamma):
		self.valFunc = np.zeros((NUM_STATES,1), dtype=np.int)
		self.transitionMatrix = np.zeros((NUM_STATES,NUM_STATES,3))
		self.rewardMatrix = np.ones((NUM_STATES,1), dtype=np.int)*-1
		self.setRewards()
		self.probabilityMatrix = np.zeros((NUM_STATES,NUM_STATES,3)) / (NUM_STATES)
		self.gamma = gamma
		
	def getID(self):
		return 'controller1'
		
	def setRewards(self):
		for i in range (0,64):
			self.rewardMatrix[i] = 5
		self.rewardMatrix[DEATH_STATE] = -50
		
	def loadValFunc(self, file_name):
		self.valFunc = np.load(file_name)
			
	def saveValFunc(self, file_name):
		np.save(file_name, self.valFunc)
		
	def loadTransitionMatrix(self, file_name):
		self.transitionMatrix = np.load(file_name)
		self.updateProbabilityMatrix()
			
	def saveTransitionMatrix(self, file_name):
		np.save(file_name, self.transitionMatrix)
		
	def getAction(self, x, y, dir, fruitX, fruitY, turn1, turn2, turn3, is_dead):
		curState = self.getState(x, y, dir, fruitX, fruitY, turn1, turn2, turn3, is_dead)
		self.transitionMatrix[self.prevState, curState, self.prevAction] = \
			self.transitionMatrix[self.prevState, curState, self.prevAction] + 1
		turnLeft = np.dot(self.probabilityMatrix[curState,:,0],self.valFunc)
		turnRight = np.dot(self.probabilityMatrix[curState,:,1],self.valFunc)
		goForward = np.dot(self.probabilityMatrix[curState,:,2],self.valFunc)
		num = randint(1,100)
		if num <= RANDOM_MOVE_PERCENT:
			action = randint(0,2)
		elif turnLeft > turnRight and turnLeft > goForward:
			action = 0 #ACTION.LEFT.value
		elif turnRight > turnLeft and turnRight > goForward:
			action = 1 #ACTION.RIGHT.value
		elif goForward > turnLeft and goForward > turnRight:
			action = 2 #ACTION.FORWARD.value
		elif turnLeft == turnRight:
			action = randint(0,1)
		elif turnRight == goForward:
			action = randint(1,2)
		elif turnLeft == goForward:
			action = 2*randint(0,1)
		else:
			action = randint(0,2)
		if curState == DEATH_STATE:
			self.updateProbabilityMatrix()
			self.updateValFunc()	
		self.prevState = curState
		self.prevAction = action
		return action
	
	def updateProbabilityMatrix(self):
		for i in range (0,NUM_STATES):
			for j in range (0,3):
				if np.sum(self.transitionMatrix[i,:,j]) > 0:
					self.probabilityMatrix[i,:,j] = self.transitionMatrix[i,:,j]/np.sum(self.transitionMatrix[i,:,j])
					
	def updateValFunc(self):
		self.valFunc = self.rewardMatrix + self.gamma * np.maximum(np.dot(self.probabilityMatrix[:,:,0],self.valFunc), \
			np.maximum(np.dot(self.probabilityMatrix[:,:,1],self.valFunc),np.dot(self.probabilityMatrix[:,:,2],self.valFunc)))
	
	def getState(self, x, y, dir, fruitX, fruitY, turn1, turn2, turn3, is_dead):
		north_west = (x-1 < 0) or (y-1 < 0) or (gameBoard[x-1][y-1] == 2)
		north = (y-1 < 0) or (gameBoard[x][y-1] == 2)
		north_east = (x+1 >= BOARD_WIDTH) or (y-1 < 0) or (gameBoard[x+1][y-1] == 2)
		east = (x+1 >= BOARD_WIDTH) or (gameBoard[x+1][y] == 2)
		south_east = (x+1 >= BOARD_WIDTH) or (y+1 >= BOARD_HEIGHT) or (gameBoard[x+1][y+1] == 2)
		south = (y+1 >= BOARD_HEIGHT) or (gameBoard[x][y+1] == 2)
		south_west = (x-1 < 0) or (y+1 >= BOARD_HEIGHT) or (gameBoard[x-1][y+1] == 2)
		west = (x-1 < 0) or (gameBoard[x-1][y] == 2)
		
		northFeature = north or (north_east and north_west)
		eastFeature = east or (north_east and south_east)
		southFeature = south or (south_east and south_west)
		westFeature = west or (north_west and south_west)
		
		if dir == DIR.NORTH.value:
			front = northFeature
			right = eastFeature
			left = westFeature
		elif dir == DIR.EAST.value:
			front = eastFeature
			right = southFeature
			left = northFeature
		elif dir == DIR.SOUTH.value:
			front = southFeature
			right = westFeature
			left = eastFeature
		else:
			front = westFeature
			right = northFeature
			left = southFeature
		
		fruit_dir = self.getFruitDir(fruitX-x, fruitY-y, dir)
		return self.stateMapping(left, right, front, turn1, turn2, turn3, fruit_dir, is_dead) 

	def stateMapping(self, left, right, front, turn1, turn2, turn3, fruit_dir, is_dead):
		if is_dead:
			return DEATH_STATE
		else:
			return left + (2*right) + (2*2*front) + (2*2*2*turn3) + \
				+ (2*2*2*2*turn2) + (2*2*2*2*2*turn1) + (2*2*2*2*2*2*fruit_dir)
	
	def getFruitDir(self, xVec, yVec, dir):
		if xVec == 0 and yVec == 0:
			return RELPOS.C.value
		elif dir == DIR.SOUTH.value:
			if xVec < 0:
				if yVec < 0:
					return RELPOS.BR.value
				elif yVec == 0:
					return RELPOS.R.value
				else:
					return RELPOS.FR.value
			elif xVec == 0:
				if yVec < 0:
					return RELPOS.B.value
				else:
					return RELPOS.F.value
			else:		
				if yVec < 0:
					return RELPOS.BL.value
				elif yVec == 0:
					return RELPOS.L.value
				else:
					return RELPOS.FL.value
		elif dir == DIR.EAST.value:
			if xVec < 0:
				if yVec < 0:
					return RELPOS.BL.value
				elif yVec == 0:
					return RELPOS.B.value
				else:
					return RELPOS.BR.value
			elif xVec == 0:
				if yVec < 0:
					return RELPOS.L.value
				else:
					return RELPOS.R.value
			else:		
				if yVec < 0:
					return RELPOS.FL.value
				elif yVec == 0:
					return RELPOS.F.value
				else:
					return RELPOS.FR.value
		elif dir == DIR.NORTH.value:
			if xVec < 0:
				if yVec < 0:
					return RELPOS.FL.value
				elif yVec == 0:
					return RELPOS.L.value
				else:
					return RELPOS.BL.value
			elif xVec == 0:
				if yVec < 0:
					return RELPOS.F.value
				else:
					return RELPOS.B.value
			else:		
				if yVec < 0:
					return RELPOS.FR.value
				elif yVec == 0:
					return RELPOS.R.value
				else:
					return RELPOS.BR.value
		else:
			if xVec < 0:
				if yVec < 0:
					return RELPOS.FR.value
				elif yVec == 0:
					return RELPOS.F.value
				else:
					return RELPOS.FL.value
			elif xVec == 0:
				if yVec < 0:
					return RELPOS.R.value
				else:
					return RELPOS.L.value
			else:		
				if yVec < 0:
					return RELPOS.BR.value
				elif yVec == 0:
					return RELPOS.B.value
				else:
					return RELPOS.BL.value
