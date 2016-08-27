from global_vars import *
from snake import Snake
from fruit import Fruit
from controller1 import Controller
import os.path
import pygame
from random import randint
import time

class Game:
	BG_COLOR = pygame.Color(255,255,255)
	snakes = []
	controllers = []
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
			self.controllers.append(Controller(GAMMA))
			if os.path.isfile('data/valFunc_' + self.controllers[i].getID() + '.npy') and \
				os.path.isfile('data/transitionMatrix_' + self.controllers[i].getID() + '.npy'):
				self.controllers[i].loadValFunc('data/valFunc_' + self.controllers[i].getID() + '.npy')
				self.controllers[i].loadTransitionMatrix('data/transitionMatrix_' + self.controllers[i].getID() + '.npy')
			newPlayer.drawSpawn(self.surf,BLOCK_SIZE)
		openCell = self.getOpenCell()
		self.fruit.moveFruit(openCell[0],openCell[1])
		self.fruit.drawFruit(self.surf,BLOCK_SIZE)

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
			action = self.controllers[i].getAction(snakeState[0], snakeState[1], curDir,
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
		for i in range(0,NUM_SNAKES):
			self.controllers[i].saveValFunc('data/valFunc_' + self.controllers[i].getID() + '.npy')
			self.controllers[i].saveTransitionMatrix('data/transitionMatrix_' + self.controllers[i].getID() + '.npy')
		pygame.quit()
			
game = Game()
game.execute();