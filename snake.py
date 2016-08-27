import pygame
from collections import deque
from global_vars import *

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
