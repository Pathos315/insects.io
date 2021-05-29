import pygame as pg
from pygame import display
from settings import *

vec = pg.math.Vector2

def collide_hit_rect(one, two):
	return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
	if dir == "x":
		hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
		
		if hits:
			if hits[0].rect.centerx > sprite.hit_rect.centerx: 
				sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2.0
			if hits[0].rect.centerx < sprite.hit_rect.centerx:
				sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2.0
			sprite.vel.x = 0
			sprite.hit_rect.centerx = sprite.pos.x
	
	if dir == "y":
		hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
		
		if hits:
			if hits[0].rect.centery > sprite.hit_rect.centery: 
				sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2.0
			if hits[0].rect.centery < sprite.hit_rect.centery:
				sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2.0
			sprite.vel.y = 0
			sprite.hit_rect.centery = sprite.pos.y

class Player(pg.sprite.Sprite):
	"""The player class"""
	def __init__(self, game, x, y):
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		
		self.game = game
		self.original_image = game.LADYBUG.convert_alpha()
		self.image = self.original_image.copy()
		
		self.rect = self.image.get_rect()
		self.hit_rect = self.rect
		
		self.pos = vec(x, y)
		self.vel = vec(0, MAX_SPEED)
		self.acc = vec(0, 0)
		self.direction = vec(0, -1)

		self.rect.center = self.pos
		
		steer, dist = self.seek_with_approach(pg.mouse.get_pos())
		angle = self.direction.angle_to(steer)
		self.rotate(angle)
	
	def seek_with_approach(self, target):
		screen_pos = vec()
		screen_pos.x = self.pos.x
		screen_pos.y = self.pos.y
				
		self.game.camera.update_rect(screen_pos)
		
		self.desired = (target - screen_pos)
		
		dist = self.desired.length()
		if dist != 0:
			self.desired.normalize_ip()
			
		if dist < APPROACH_RADIUS:
			self.desired *= dist * MAX_SPEED
		else:
			self.desired *= MAX_SPEED
		
		steer = (self.desired - self.vel)
		
		if steer.length() > MAX_FORCE:
			steer.scale_to_length(MAX_FORCE)
	
		if dist != 0:
			angle = self.direction.angle_to(steer)
			self.rotate(angle)
		
		steer *= 10
		return steer, dist

	def update(self):
		self.vel = vec(0,0)
		steer, dist = self.seek_with_approach(pg.mouse.get_pos())
		if dist > 0:
			angle = self.direction.angle_to(steer)
			self.rotate(angle)
	
		self.acc = steer
		self.vel += self.acc
		self.pos += self.vel

		collide_with_walls(self, self.game.platforms, "x")
		self.hit_rect.centery = self.pos.y
		collide_with_walls(self, self.game.platforms, "y")		
		self.rect.center = self.hit_rect.center
	
		self.rect.center = self.pos
		self.rect.clamp_ip(self.game.background_rect)
		
	def rotate(self, angle):
		self.image = pg.transform.rotozoom(self.original_image, -angle, 1)

	def draw(self, surf):
		surf.blit(self.image, self.rect)

class Platform(pg.sprite.Sprite):
	"""Governs the appearance of all platforms"""
	def __init__(self, game, platform_type, x, y, WIDTH, HEIGHT):
		self.groups = game.platforms, game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		
		self.game = game
		self.image = pg.Surface((WIDTH, HEIGHT))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.type = platform_type
		self.mask = pg.mask.from_surface(self.image)
		
		if self.type == Earth:
			self.color = SOIL
		elif self.type == Grass:
			self.color = LEAF
		elif self.type == Topsoil:
			self.color = DIRT

		self.image.fill(self.color)