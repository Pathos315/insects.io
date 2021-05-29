import pygame as pg
from pygame.constants import MOUSEBUTTONDOWN

import sys
import math
from random import randint, uniform
from os import path

from settings import *
from sprites import *

vec = pg.math.Vector2

pg.init()
pg.display.set_caption("Insect Game Concept")
clock = pg.time.Clock()

background = pg.Surface((BG_WIDTH, BG_HEIGHT))



LADYBUG_PATH = path.join(path.dirname(__file__), "210528_walking.png")

# Create classes

class Camera(object):
	def __init__(self, width, height):
		self.rect = pg.Rect(0,0, width, height)
		self.width = width
		self.height = height
		
	def update(self, target):
		x = target.rect.centerx - int(WIDTH/2)
		y = target.rect.centery - int(HEIGHT/2)
	
		# limit scrolling
		x = max(0, x) # left
		y = max(0, y) # top
	
		x = min((BG_WIDTH - WIDTH), x)
		y = min((BG_HEIGHT - HEIGHT), y)
		
		self.rect = pg.Rect(x, y, self.width, self.height)
	
	def update_rect(self, target):
		target.x -= self.rect.x
		target.y -= self.rect.y
		
		
class Game():
	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((WIDTH, HEIGHT))
		self.clock = pg.time.Clock()
		self.FPS = 60

	def new(self):
		self.load_images()
		self.background_rect = background.get_rect()
				
		self.platforms = pg.sprite.Group()
		self.all_sprites = pg.sprite.Group()
			
		for data in platform_data:
			Platform(self, *data)
			
		Platform(self, Earth, 0, 0, 20, 600)
		self.camera = Camera(BG_WIDTH, BG_HEIGHT)
		self.player = Player(self, SCREEN_HW, SCREEN_HH)
		self.show_vectors = False

	def load_images(self):
		self.LADYBUG = pg.image.load(LADYBUG_PATH)

	def run(self):
	# Main game loop
		self.playing = True
		while self.playing:
			self.dt = clock.tick(self.FPS) / 1000
			self.events()
			self.update()
			self.draw()

	def quit(self):
		pg.quit()
		sys.exit()

	def update(self):
		self.all_sprites.update()
		self.camera.update(self.player)
	
	def draw(self):
		background.fill(SKY)
		self.all_sprites.draw(background)
		self.screen.blit(background, (0,0), self.camera.rect)
		if self.show_vectors:
			self.player.draw_vectors()
		pg.display.flip()

	def events(self):
		for event in pg.event.get():
			if event.type == pg.QUIT: 
				sys.exit()
			
					
g = Game()

while g.run:
	g.new()
	g.run()

pg.quit()
