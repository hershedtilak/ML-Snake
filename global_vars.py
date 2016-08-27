import numpy as np
from enum import Enum

RANDOM_MOVE_PERCENT = 0
UPDATE_INTERVAL = 15 # in milliseconds
NUM_SNAKES = 1
BOARD_WIDTH = 30
BOARD_HEIGHT = 30
BLOCK_SIZE = 10
GAMMA = 0.9

NUM_STATES = 577
DEATH_STATE = 576

gameBoard = np.zeros((BOARD_WIDTH,BOARD_HEIGHT), dtype=np.int)
				
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
