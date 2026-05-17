import pygame
from pygame.locals import *
from constants import *
from sprites import PacmanSprites
from entity import Entity


class Pacman(Entity):
    def __init__(self, node, level=0):
        Entity.__init__(self, node)
        self.level = level
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.set_speed(level_speed(self.level, "pacman"))
        self.sprites = PacmanSprites(self)

        # AI Control Variables
        self.ai_mode = True
        self.ai_direction = STOP

    def update(self, dt):
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.get_valid_key()
        if self.overshot_target():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.get_new_target(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.get_new_target(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.set_position()
        else:
            if self.opposite_direction(direction):
                self.reverse_direction()

    def get_valid_key(self):
        # If AI mode is on, return the AI's chosen direction!
        if self.ai_mode:
            return self.ai_direction

        # Otherwise, check keyboard as normal
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def eat_pellets(self, pellet_list):
        for pellet in pellet_list:
            if self.collide_check(pellet):
                return pellet
        return None

    def collide_ghost(self, ghost):
        return self.collide_check(ghost)

    def collide_check(self, other):
        d = self.position - other.position
        d_squared = d.magnitude_squared()
        r_squared = (self.collide_radius + other.collide_radius) ** 2
        if d_squared < r_squared:
            return True
        return False

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.image = self.sprites.get_start_image()
        self.sprites.reset()
        self.set_speed(level_speed(self.level, "pacman"))

    def die(self):
        self.alive = False
        self.direction = STOP