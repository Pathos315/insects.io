import pygame as pg
import sys
import math
from random import randint, uniform
from os import path

from pygame.constants import MOUSEBUTTONDOWN
vec = pg.math.Vector2

#### CONSTANTS

#Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LEAF = (173, 148, 56)
SOIL = ( 73, 56, 41)
SKY = (252, 238, 220)

#DISPLAY
SCREEN_W = 800
SCREEN_H = 600
SCREEN_HW = SCREEN_W * 0.5
SCREEN_HH = SCREEN_H * 0.5
SCREEN_MID = vec(SCREEN_HW, SCREEN_HH)

#BACKGROUND
bg_w = 3000
bg_h = 1000
bg_hw = bg_w * 0.5
bg_hh = bg_h * 0.5
bg_size = (bg_w, bg_h)
background = pg.Surface((bg_size))

#Images
LADYBUG_PATH = path.join(path.dirname(__file__), "210502_ladybug.png")
LADYBUG = pg.image.load(LADYBUG_PATH)
FPS = 60

#Forces
MAX_SPEED = 5
MAX_FORCE = 0.2
APPROACH_RADIUS = 120
GRAVITY = 1

#Color Constants
LEAF = (173, 148, 56)
SOIL = ( 73, 56, 41)
SKY = (252, 238, 220)
DIRT = (253, 207, 154)
BLACK = (0,0,0)
GREEN = (155,155,50)
WHITE = (250,250,250)
RED = (255,0,0)

#### Create classes

class Entity():
	"""The overarching class, governing how all objects are rendered in the camera"""
	def __init__(self, x, y, width, height) -> None:
		self.game = g
		self.vel = vec(0,0)
		self.pos = vec(x,y)
		self.width = width
		self.height = height
		self.image = []
		self.color = BLACK
		self.friction = 0.9
		self.lift = 0
		self.gravity = GRAVITY - self.lift
		
	def goto(self, x, y):
		self.pos = vec(x,y)

	def render(self):
		background.blit(self.image, self.rect)

	def is_aabb_collision(self, other):
		# Axis Aligned Bounding Box
		x_collision = (math.fabs(self.pos[0] - other.pos[0]) * 2) < (self.width + other.width)
		y_collision = (math.fabs(self.pos[1] - other.pos[1]) * 2) < (self.height + other.height)
		return (x_collision and y_collision)
		
class Player(Entity):
	"""The player class"""
	def __init__(self, x, y, width, height):
		super().__init__(x, y, width, height)
		self.image0 = pg.Surface((32, 48))
		self.image0 = LADYBUG.convert_alpha()
		self.rect0 = self.image0.get_rect()
		self.image = self.image0.copy()
		self.rect = self.image.get_rect()
		self.image = LADYBUG.convert_alpha()
		self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
		self.pos = SCREEN_HW, SCREEN_HH
		self.rect.center = self.pos
		self.lift = 0.9
		self.friction = 0.9

	def flying(self): False

	def seek_with_approach(self, target):
		self.desired = target - self.pos
		self.dist = self.desired.length()
		self.desired.normalize_ip()
		if self.dist < APPROACH_RADIUS:
			self.desired *= self.dist / APPROACH_RADIUS * MAX_SPEED
		else:
			self.desired *= MAX_SPEED
		self.steer = (self.desired - self.vel)
		if self.steer.length() > MAX_FORCE:
			self.steer.scale_to_length(MAX_FORCE)
		return self.steer

	def update(self):
		self.acc = self.seek_with_approach(self.mpos)
		self.vel += self.acc
		self.vel[1] += self.gravity
		self.pos += self.vel
		self.rect.center = self.pos
		self.rect.clamp_ip(background.get_rect())

	def draw(self, surf):
		surf.blit(self.image, self.rect)

	def rotate(self):
		self.mpos = pg.mouse.get_pos()
		self.rel = (self.mpos[0] - self.pos[0]), (self.mpos[1] - self.pos[1])
		self.angle = (180 / math.pi) * -math.atan2(self.rel[1], self.rel[0])
		self.image = pg.transform.rotozoom(self.image0, int(self.angle)-90, 1)

	def draw_vectors(self):
		scale = 25
		# vel
		pg.draw.line(g.screen, GREEN, SCREEN_MID, vec(self.pos + self.vel * scale), 5)
		# desired
		pg.draw.line(g.screen, RED, SCREEN_MID, vec(self.pos + self.desired * scale), 5)
		# approach radius
		pg.draw.circle(g.screen, BLACK, vec(self.mpos), APPROACH_RADIUS, 1)

class Camera(object):
	def __init__(self, width, height):
		self.rect = pg.Rect(0,0, width, height)
		self.width = width
		self.height = height
		
	def update(self, target):
		x = target.rect.centerx - int(SCREEN_HW)
		y = target.rect.centery - int(SCREEN_HH)
	
		# limit scrolling
		x = max(0, x) # left
		y = max(0, y) # top
	
		x = min(bg_w - SCREEN_W, x)
		y = min(bg_h - SCREEN_H, y)
		
		self.rect = pg.Rect(x, y, self.width, self.height)

class Platform(Entity):
	"""Governs the appearance of all platforms"""
	def __init__(self, platform_type, x, y, width, height):
		self.image = pg.Surface((width, height))
		self.rect = self.image.get_rect()
		self.rect.width = width
		self.rect.height = height
		self.rect.x, self.rect.y = (x,y)
		self.pos = (self.rect.x, self.rect.y)
		self.type = platform_type

		if self.type == "Earth":
			self.color = SOIL
		elif self.type == "Grass":
			self.color = LEAF
		elif self.type == "Topsoil":
			self.color = DIRT

		self.image.fill(self.color)

class Game():
	"""The game loop"""
	def __init__(self):
		# Instantiates the game
		pg.init()
		pg.display.set_caption("Insect Game Concept")
		self.screen = pg.display.set_mode((SCREEN_W, SCREEN_H))

	def new(self):
		# Generates the players and the platforms
		self.player = Player(600, 0, 48, 64)
		self.blocks = [Platform("Earth", bg_hw,bg_hh,bg_w,bg_hh)]
		self.groundcover = [Platform("Topsoil", bg_hw,bg_hh-200,bg_w,200)]
		self.camera = Camera(SCREEN_W, SCREEN_H)
		self.show_vectors = False
		self.leaves = []

		for i in range(50):
			x = randint(0, bg_w)
			y = randint(0, bg_h)
			
			w = randint(50, 100)
			h = 20
			
			s = pg.Surface((w,h))
			s.fill(LEAF)
			r = s.get_rect()
			r.x = x
			r.y = y
			
			self.leaves.append((s, r))
			background.blit(s, r)


	def run(self):
	# Runs the main game loop
		self.playing = True
		while self.playing:
			self.clock = pg.time.Clock()
			self.FPS = FPS
			self.dt = self.clock.tick(self.FPS) / 1000
			self.events()
			self.update()
			self.draw()

	def quit(self):
	# Quits the game
		pg.quit()
		sys.exit()

	def update(self):
	# Updates the player and camera
		self.player.update()
		self.camera.update(self.player)

	def draw(self):
	# Draws the game through the camera
		#Layer 0
		background.fill(SKY)

		#Layer 1
		for ground in self.groundcover:
			ground.render(self.camera)

		#Layer 2
		for leaf in self.leaves:
			leaf.render(self.camera)
			
		#Layer 3
		self.player.render()
		self.camera.update(self.player)
		#Layer 4
		for block in self.blocks:
			block.render(self.camera)
		
		if self.show_vectors:
			self.player.draw_vectors()

		self.screen.blit(background, (0,0), self.camera.rect)
		pg.display.flip()

	def events(self):
	# More game loop stuff
		for event in pg.event.get():
			if event.type == pg.QUIT: 
				sys.exit()
			
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_v:
					self.show_vectors = not self.show_vectors
				if event.key == pg.K_SPACE:
					self.player.flying = not self.player.flying

			if event.type == pg.MOUSEMOTION:
				self.player.rotate()

		# Checks for collisions
		for block in self.blocks:
			if self.player.is_aabb_collision(block):
				# self.Player is to the left
				if self.player.pos[0] < block.pos[0] - block.width * 0.5 and self.player.vel[0] > 0:
					self.player.vel[0] = 0
					self.player.pos[0] = block.pos[0] - block.width * 0.5 - self.player.width * 0.5
				# self.Player is to the right
				elif self.player.pos[0] > block.pos[0] + block.width * 0.5 and self.player.vel[0] < 0:
					self.player.vel[0] = 0
					self.player.pos[0] = block.pos[0] + block.width * 0.5 + self.player.width * 0.5
				# self.Player is above
				elif self.player.pos[1] < block.pos[1]:
					self.player.pos[1] = (block.pos[1] - block.height * 0.5 - self.player.height * 0.5) - 1
					if self.player.flying == False:  # If the player isn't flying, they're stuck to the ground.
						self.player.vel[1] = 0  # If the player is flying, they ignore the ground.
					else:
						pass
						
				# self.Player is below
				elif self.player.pos[1] > block.pos[1]:
					self.player.vel[1] = 0
					self.player.pos[1] = block.pos[1] + block.height * 0.5 + self.player.height * 0.5 

		# Check for groundcover contact
		for ground in self.groundcover:
			if self.player.is_aabb_collision(ground):
				# self.Player is above
				if self.player.flying == False:
					if self.player.pos[1] > ground.pos[1]:
						self.player.vel[1] = 0
						self.player.pos[1] = (ground.pos[1] - (ground.height * 0.5) - (self.player.height * 0.5)) + 1
				else:
					pass

		if self.player.flying:
			self.player.gravity = GRAVITY - self.player.lift
			print("You are flying")

		else:

			if self.player.pos[1] < ground.pos[1] - ground.height * 0.5 - self.player.height * 0.5 + 1:   #check if player is still in the air
				self.player.gravity = GRAVITY
				print("You are falling")
			else:
				self.player.gravity = 0
				print("You are walking")
				
				
		# Border check the self.player

		# y axis
		if self.player.pos[1] < 0:
			self.player.pos[1] = 0
		if self.player.pos[1] > bg_h:
			self.player.pos[1] = bg_h
		# x axis
		if self.player.pos[0] < 0:
			self.player.pos[0] = 0
		if self.player.pos[0] > bg_w:
			self.player.pos[0] = bg_w

g = Game()

while g.run:
	g.new()
	g.run()

pg.quit()
