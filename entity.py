import pygame
from vector import Vector
from constants import *
from random import randint

class Entity(object):
    """
    This is a generic class with methods that both Pacman and the ghosts will inherit.
    This class has all the general updates and movement functionality, making it so
    the entity will only move along the nodes, but their specific behaviors may change
    in their own classes.
    """
    def __init__(self, node):
        self.speed = None
        self.target = None
        self.start_node = None
        self.node = None
        self.position = None
        self.name = None
        self.directions = {UP:Vector(0, -1), DOWN:Vector(0, 1), LEFT:Vector(-1, 0), RIGHT:Vector(1, 0), STOP:Vector(0, 0)}
        self.direction = STOP
        self.radius = 10
        self.collide_radius = 5
        self.color = WHITE
        self.visible = True
        self.disable_portal = False
        self.goal = None
        self.direction_method = self.random_direction
        self.set_start_node(node)
        self.image = None

    def set_position(self):
        """Set the position of the entity"""
        self.position = self.node.position.copy()

    def valid_direction(self, direction):
        """Check if the given direction is valid"""
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False

    def get_new_target(self, direction):
        """Get the new target position if going in a valid direction"""
        if self.valid_direction(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshot_target(self):
        """Check if entity overshoots the target"""
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitude_squared()
            node2Self = vec2.magnitude_squared()
            return node2Self >= node2Target
        return False

    def reverse_direction(self):
        """Reverse the direction of the entity"""
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def opposite_direction(self, direction):
        """Get the opposite direction of the entity"""
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def set_speed(self, speed):
        """Set the speed of the entity"""
        self.speed = speed * TILEWIDTH / 16

    def render(self, screen):
        """Render the entity"""
        if self.visible:
            if self.image is not None:
                adjust = Vector(TILEWIDTH, TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.as_tuple())
            else: 
                p = self.position.as_int()
                pygame.draw.circle(screen, self.color, p, self.radius)

    def update(self,dt):
        """
        When the entity gets to a node,
        then it will just choose a random direction to go next.
        """
        self.position += self.directions[self.direction] * self.speed * dt

        if self.overshot_target():
            self.node = self.target
            directions = self.valid_directions()
            direction = self.direction_method(directions)
            if not self.disable_portal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]
            self.target = self.get_new_target(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.get_new_target(self.direction)

            self.set_position()

    def valid_directions(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.valid_direction(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    @staticmethod
    def random_direction(directions):
        return directions[randint(0, len(directions) - 1)]

    def goal_direction(self, directions):
        distances = []
        for direction in directions:
            vec = self.node.position + self.directions[direction] * TILEWIDTH - self.goal
            distances.append(vec.magnitude_squared())
        index = distances.index(min(distances))
        return directions[index]

    def set_start_node(self, node):
        self.node = node
        self.start_node = node
        self.target = node
        self.set_position()

    def set_between_nodes(self, direction):
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.target.position + self.node.position) / 2

    def reset(self):
        self.set_start_node(self.start_node)
        self.direction = STOP
        self.visible = True
