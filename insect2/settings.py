# settings

BG_WIDTH = 5000 #1200
BG_HEIGHT = 1000 #800

WIDTH = 800
HEIGHT = 600

SCREEN_HW = WIDTH * 0.5
SCREEN_HH = HEIGHT * 0.5
SCREEN_MID = (SCREEN_HW, SCREEN_HH)
GRAVITY = 0.05

#Color Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

DIRT = (253, 207, 154)
SOIL = (73, 56, 41)
LEAF = (173, 148, 56)
SKY = (252, 238, 220)

FPS = 60

MAX_SPEED = 5
MAX_FORCE = 0.4
APPROACH_RADIUS = 120

# platform types
Earth = 0
Topsoil = 1
Grass = 2

friction = 0.9
lift = 0
gravity = GRAVITY - lift

platform_data = [(Earth, 0, BG_HEIGHT, BG_WIDTH, BG_HEIGHT * 0.5), 
		         (Grass, 600, 400, 600, 20), 
			     (Earth, 600, 600, 1000, 20),
			     (Topsoil,0, BG_HEIGHT-200, BG_WIDTH, (BG_HEIGHT * 0.5)-200),
			     (Grass, 200, 500, 100, 200)]