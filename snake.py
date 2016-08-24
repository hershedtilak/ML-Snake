import pygame
import numpy as np
from collections import deque
from enum import Enum
from random import randint
import time

FIRST_RUN = False
RANDOM_MOVE_PERCENT = 0
UPDATE_INTERVAL = 15 # in milliseconds
NUM_SNAKES = 1
BOARD_WIDTH = 25
BOARD_HEIGHT = 25
BLOCK_SIZE = 10
GAMMA = 0.9

NUM_STATES = 577
DEATH_STATE = 576

gameBoard = np.zeros((BOARD_WIDTH,BOARD_HEIGHT), dtype=np.int)

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
					
class CELL(Enum):
	EMPTY = 0
	FRUIT = 1
	BAD = 2

class DIR(Enum):
	NORTH = 0
	SOUTH = 1
	EAST = 2
	WEST = 3
	
# C=Center F=Forward R=Right L=Left B=Back
class RELPOS(Enum):
	C = 0
	F = 1
	R = 2
	L = 3
	B = 4
	BR = 5
	FR = 6
	BL = 7
	FL = 8
	
class ACTION(Enum):
	LEFT = 0
	RIGHT = 1
	FORWARD = 2
	
class Fruit:
	color = pygame.Color(0,255,0)
	def moveFruit(self,x,y):
		self.x = x
		self.y = y
		gameBoard[x][y] = CELL.FRUIT.value
	
	def drawFruit(self,surface,blockSize):
		surface.fill(self.color, pygame.Rect((self.x*blockSize, self.y*blockSize), (blockSize, blockSize)))
		
	def getX(self):
		return self.x
		
	def getY(self):
		return self.y

class Snake:

	def __init__(self, x, y, dir, snake_color, bg_color):
		self.xPos = deque([])
		self.yPos = deque([])
		self.length = 1
		self.xPos.append(x)
		self.yPos.append(y)
		self.isDead = False
		self.ateFruit = False
		self.lastTailX = None
		self.lastTailY = None
		self.lastThreeTurns = deque([0,1,0])
		gameBoard[x][y] = CELL.BAD.value
		self.dir = dir
		self.snake_color = snake_color
		self.bg_color = bg_color
	
	def updateFruit(self):
		self.ateFruit = False

	def update(self):
		if self.dir == DIR.NORTH.value:
			newX = self.xPos[-1]
			newY = self.yPos[-1]-1
		elif self.dir == DIR.SOUTH.value:
			newX = self.xPos[-1]
			newY = self.yPos[-1]+1
		elif self.dir == DIR.EAST.value:
			newX = self.xPos[-1]+1
			newY = self.yPos[-1]
		else:
			newX = self.xPos[-1]-1
			newY = self.yPos[-1]
		
		if newX < 0 or newX >= BOARD_WIDTH or newY < 0 or newY >= BOARD_HEIGHT:
			self.isDead = True
		elif gameBoard[newX][newY] == CELL.BAD.value:
			self.isDead = True	
		else:
			if gameBoard[newX][newY] != CELL.FRUIT.value:
				self.lastTailX = self.xPos.popleft()
				self.lastTailY = self.yPos.popleft()
				gameBoard[self.lastTailX][self.lastTailY] = CELL.EMPTY.value
			else:
				self.ateFruit = True
				self.length = self.length + 1
			self.xPos.append(newX)
			self.yPos.append(newY)
			gameBoard[newX][newY] = CELL.BAD.value
	
	def setDir(self, dir):
		self.dir = dir
	
	def updateTurnQueue(self, turn):
		self.lastThreeTurns.popleft()
		self.lastThreeTurns.append(turn)
	
	def reset(self, x, y, dir):
		self.xPos.clear()
		self.yPos.clear()
		self.xPos.append(x)
		self.yPos.append(y)	
		gameBoard[x][y] = CELL.BAD.value
		self.dir = dir
		self.length = 1
		self.isDead = False
		
	def removeFromBoard(self):
		for i in range (0,self.length):
			gameBoard[self.xPos[i]][self.yPos[i]] = CELL.EMPTY.value
	
	def drawSpawn(self, surface, blockSize):
		surface.fill(self.snake_color, pygame.Rect((self.xPos[-1]*blockSize, self.yPos[-1]*blockSize), (blockSize, blockSize)))

	def drawFruit(self, surface, blockSize):
		surface.fill(self.snake_color, pygame.Rect((self.xPos[-1]*blockSize, self.yPos[-1]*blockSize), (blockSize, blockSize)))
		
	def drawNormal(self, surface, blockSize):
		surface.fill(self.snake_color, pygame.Rect((self.xPos[-1]*blockSize, self.yPos[-1]*blockSize), (blockSize, blockSize)))
		surface.fill(self.bg_color, pygame.Rect((self.lastTailX*blockSize, self.lastTailY*blockSize), (blockSize, blockSize)))
		
	def drawDead(self, surface, blockSize):
		for i in range (0,self.length):
			surface.fill(self.bg_color, pygame.Rect((self.xPos[i]*blockSize, self.yPos[i]*blockSize), (blockSize, blockSize)))
		if self.lastTailX != None and self.lastTailY != None:
			surface.fill(self.bg_color, pygame.Rect((self.lastTailX*blockSize, self.lastTailY*blockSize), (blockSize, blockSize)))
			
	def getState(self):
		return [self.xPos[-1], self.yPos[-1], self.dir, self.lastThreeTurns[0], self.lastThreeTurns[1], self.lastThreeTurns[2]]

class Game:
	BG_COLOR = pygame.Color(255,255,255)
	snakes = []
	controller = Controller(GAMMA)
	fruit = Fruit()
	running = True
	surf = pygame.display.set_mode((BOARD_WIDTH*BLOCK_SIZE,BOARD_HEIGHT*BLOCK_SIZE), pygame.HWSURFACE)
	
	def __init__(self):
		self.surf.fill(self.BG_COLOR)
		for i in range (0,NUM_SNAKES):
			startDir = randint(0,3)
			openCell = self.getOpenCell()
			newPlayer = Snake(openCell[0],openCell[1],startDir,pygame.Color(20*i,0,50*i),self.BG_COLOR)
			self.snakes.append(newPlayer)
			newPlayer.drawSpawn(self.surf,BLOCK_SIZE)
		openCell = self.getOpenCell()
		self.fruit.moveFruit(openCell[0],openCell[1])
		self.fruit.drawFruit(self.surf,BLOCK_SIZE)
		if FIRST_RUN == False:
			self.controller.loadValFunc('valFunc.npy')
			self.controller.loadTransitionMatrix('transitionMatrix.npy')
			
	def getOpenCell(self):
		x = randint(0,BOARD_WIDTH-1)
		y = randint(0,BOARD_HEIGHT-1)
		while gameBoard[x][y] != CELL.EMPTY.value:
			x = randint(0,BOARD_WIDTH-1)
			y = randint(0,BOARD_HEIGHT-1)
		return [x,y]
	
	def getNextDir(self, action, curDir):
		if action == ACTION.LEFT.value:
			if curDir == DIR.NORTH.value:
				return DIR.WEST.value
			elif curDir == DIR.EAST.value:
				return DIR.NORTH.value
			elif curDir == DIR.SOUTH.value:
				return DIR.EAST.value
			else:
				return DIR.SOUTH.value
		elif action == ACTION.RIGHT.value:
			if curDir == DIR.NORTH.value:
				return DIR.EAST.value
			elif curDir == DIR.EAST.value:
				return DIR.SOUTH.value
			elif curDir == DIR.SOUTH.value:
				return DIR.WEST.value
			else:
				return DIR.NORTH.value
		else:
			return curDir

	def update(self):
		# update snake positions
		for i in range (0,NUM_SNAKES):
			self.snakes[i].update()	
		# update controller / get next moves
		for i in range (0,NUM_SNAKES):
			snakeState = self.snakes[i].getState()
			curDir = snakeState[2]
			turn1 = snakeState[3]
			turn2 = snakeState[4]
			turn3 = snakeState[5]
			action = self.controller.getAction(snakeState[0], snakeState[1], curDir,
				self.fruit.getX(), self.fruit.getY(), turn1, turn2, turn3, 
				self.snakes[i].isDead)
			if action != ACTION.FORWARD.value:
				self.snakes[i].updateTurnQueue(action)
			nextDir = self.getNextDir(action, curDir)		
			self.snakes[i].setDir(nextDir)
		# update board state
		for i in range (0,NUM_SNAKES):
			if self.snakes[i].isDead:
				self.snakes[i].removeFromBoard()
				self.snakes[i].drawDead(self.surf, BLOCK_SIZE)
				startDir = randint(0,3)
				openCell = self.getOpenCell()
				self.snakes[i].reset(openCell[0], openCell[1], startDir)
				self.snakes[i].drawSpawn(self.surf, BLOCK_SIZE)
			elif self.snakes[i].ateFruit:
				self.snakes[i].updateFruit()
				self.snakes[i].drawFruit(self.surf, BLOCK_SIZE)
				openCell = self.getOpenCell()
				self.fruit.moveFruit(openCell[0],openCell[1])
				self.fruit.drawFruit(self.surf,BLOCK_SIZE)
			else:
				self.snakes[i].drawNormal(self.surf, BLOCK_SIZE)
			
	def execute(self):
		while self.running == True:
			pygame.event.pump()
			keys = pygame.key.get_pressed()
			if keys[pygame.K_ESCAPE]:
				self.running = False
			self.update()
			pygame.display.flip()
			time.sleep (UPDATE_INTERVAL / 1000.0);
		self.controller.saveValFunc('valFunc')
		self.controller.saveTransitionMatrix('transitionMatrix')
		pygame.quit()
			
game = Game()
game.execute();