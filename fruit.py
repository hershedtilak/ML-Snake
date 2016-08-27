import pygame
from global_vars import *

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