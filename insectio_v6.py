import pygame as pg
import sys
import math
from random import randint, uniform
import numpy as np

from pygame.constants import MOUSEBUTTONDOWN
vec = pg.math.Vector2

pg.init()
pg.display.set_caption("Insect Game Concept")
clock = pg.time.Clock()

WIDTH = 1200
HEIGHT = 800
SCREEN_HW = WIDTH * 0.5
SCREEN_HH = HEIGHT * 0.5
GRAVITY = 0.05

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LEAF = (173, 148, 56)
SOIL = ( 73, 56, 41)
SKY = (252, 238, 220)

LADYBUG_PATH = "/Users/johnfallot/Coding Projects/GameIdea/Assets/210502_LadyBug.png"
LADYBUG = pg.image.load(LADYBUG_PATH)

FPS = 60

MAX_SPEED = 5
MAX_FORCE = 0.2
APPROACH_RADIUS = 120


#Color Constants
LEAF = (173, 148, 56)
SOIL = ( 73, 56, 41)
SKY = (252, 238, 220)
DIRT = (253, 207, 154)
BLACK = (0,0,0)
GREEN = (155,155,50)
WHITE = (250,250,250)
RED = (255,0,0)

# Create classes

class Entity():
    """The overarching class, governing how all objects are rendered in the camera"""
    def __init__(self, x, y, width, height) -> None:
        self.game = g
        self.vel = vec(0,0)
        self.pos = vec(x,y)
        self.width = width
        self.height = height
        self.image = []
        self.color = WHITE
        self.friction = 0.9
        self.lift = 0
        self.gravity = GRAVITY - self.lift
        
    def goto(self, x, y):
        self.pos = vec(x,y)

    def render(self, camera):
        self.xCoords = int(self.pos[0]-self.width * 0.5-camera.pos[0] + SCREEN_HW)
        self.yCoords = int(self.pos[1]-self.height * 0.5-camera.pos[1] + SCREEN_HH)
        if self.image == []:
            pg.draw.rect(g.screen, self.color, pg.Rect(self.xCoords, self.yCoords, self.width, self.height))
        else:
            pg.Surface.blit(g.screen, self.image, pg.Rect(self.xCoords, self.yCoords, self.width, self.height))

    def is_aabb_collision(self, other):
        # Axis Aligned Bounding Box
        x_collision = (math.fabs(self.pos[0] - other.pos[0]) * 2) < (self.width + other.width)
        y_collision = (math.fabs(self.pos[1] - other.pos[1]) * 2) < (self.height + other.height)
        return (x_collision and y_collision)

class Player(Entity):
    """The player class"""
    def __init__(self, x, y, width, height):
        Entity.__init__(self, x, y, width, height)
        self.image0 = pg.Surface((32, 48))
        self.image0 = LADYBUG.convert_alpha()
        self.rect0 = self.image0.get_rect()
        self.image = self.image0.copy()
        self.rect = self.image.get_rect()
        self.image = LADYBUG.convert_alpha()
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.rect.center = self.pos
        self.lift = 0.9

    def walking(self):
        if self.walking:
            self.gravity = GRAVITY
        else:
            self.gravity = GRAVITY - self.lift

    def follow_mouse(self):
        mpos = pg.mouse.get_pos()
        self.acc = (mpos - self.pos).normalize() * 0.5

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def seek_with_approach(self, target):
        self.desired = target - self.pos
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < APPROACH_RADIUS:
            self.desired *= dist / APPROACH_RADIUS * MAX_SPEED
        else:
            self.desired *= MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def update(self):
        self.acc = self.seek_with_approach(pg.mouse.get_pos())
        self.vel += self.acc
        self.vel[1] += self.gravity
        self.pos += self.vel

    def rotate(self):
        mpos = pg.mouse.get_pos()
        self.rel = (mpos[0] - self.pos[0]), (mpos[1] - self.pos[1])
        angle = (180 / math.pi) * -math.atan2(self.rel[1], self.rel[0])
        self.image = pg.transform.rotozoom(self.image0, int(angle)-90, 1)

    def draw_vectors(self):
        scale = 25
        # vel
        pg.draw.line(g.screen, GREEN, np.dot((self.rel), (math.log)), vec(self.pos + self.vel * scale), 5)
        # desired
        pg.draw.line(g.screen, RED, np.dot((self.rel), (math.log)), vec(self.pos + self.desired * scale), 5)
        # approach radius
        pg.draw.circle(g.screen, BLACK, np.dot((self.rel), (math.log)), APPROACH_RADIUS, 1)

class Camera():
    def __init__(self, target):
        self.pos = target.pos
        self.vel = target.vel
        
    def update(self, target):
        self.pos = target.pos
        self.vel = target.vel

class Platform(Entity):
    """Governs the appearance of all platforms"""
    def __init__(self, x, y, width, height) -> None:
        Entity.__init__(self, x, y, width, height)
        self.image = pg.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = (x,y)
        self.color = []

class Earth(Platform):
    """Governs the appearance of all underground tiles"""
    def __init__(self, x, y, width, height):
        Platform.__init__(self, x, y, width, height)
        self.color.append(SOIL)

class Grass(Platform):
    """Governs the appearance of all leafy and shrub tiles"""
    def __init__(self, x, y, width, height):
        Platform.__init__(self, x, y, width, height)
        self.color.append(LEAF)
        
class TopSoil(Platform):
    """Governs the appearance of all surface tiles"""
    def __init__(self, x, y, width, height):
        Platform.__init__(self, x, y, width, height)
        self.color.append(DIRT)

class Game():
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.FPS = 60

    def new(self):
        self.player = Player(600, 0, 48, 64)
        self.blocks = [(Earth(600, 200, 400, 20)), Grass(600, 400, 600, 20), Earth(600, 600, 1000, 20), TopSoil(1000, 500, 100, 200), Grass (200, 500, 100, 200)]
        self.camera = Camera(self.player)
        self.walking = self.player.walking()
        self.show_vectors = False

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
        self.player.update()
        self.camera.update(self.player)

    def draw(self):
        self.screen.fill(SKY)
        self.player.render(self.camera)
        for block in self.blocks:
            block.render(self.camera)
        if self.show_vectors:
            self.player.draw_vectors()
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_v:
                    self.show_vectors = not self.show_vectors
            if event.type == pg.MOUSEMOTION:
                self.player.rotate()

        # Check for collisions
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
                    self.player.vel[1] = 0
                    self.player.pos[1] = block.pos[1] - block.height * 0.5 - self.player.height * 0.5 + 1
                    self.player.vel[0] *= block.friction
                # self.Player is below
                elif self.player.pos[1] > block.pos[1]:
                    self.player.vel[1] = 0
                    self.player.pos[1] = block.pos[1] + block.height * 0.5 + self.player.height * 0.5 

        # Border check the self.player
        
        if self.player.pos[1] > HEIGHT * 2:
            self.player.goto(self.player.pos[0], HEIGHT * 2)
            self.player.vel[0] = 0
            self.player.vel[1] = 0
        if self.player.pos[0] > WIDTH * 2:
            self.player.goto(0, self.player.pos[1])

g = Game()

while g.run:
    g.new()
    g.run()

pg.quit()