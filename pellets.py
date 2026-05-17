import pygame
from vector import Vector
from constants import *
import numpy as np


class Pellet(object):
    """
    Object class to represent a pellet. These are the primary source of points in Pacman,
    and all are required to be eaten to complete the maze.
    """
    def __init__(self, row, column):
        self.name = PELLET
        self.position = Vector(column * TILEWIDTH, row * TILEHEIGHT)
        self.color = WHITE
        self.radius = int(2 * TILEWIDTH / 16)
        self.collide_radius = int(2 * TILEWIDTH / 16)
        self.points = 10
        self.visible = True

    def render(self, screen):
        """Renders the pellet on the screen."""
        if self.visible:
            adjust = Vector(TILEWIDTH, TILEHEIGHT) / 2
            p = self.position + adjust
            pygame.draw.circle(screen, self.color, p.as_int(), self.radius)


class PowerPellet(Pellet):
    """
    Object class representing a power pellet. Unlike regular pellets, these
    are the only way for pacman to kill the ghosts, and there are only 4 of them total.
    They are also not required to be eaten to complete the maze, but can help you earn big points.
    """
    def __init__(self, row, column):
        Pellet.__init__(self, row, column)
        self.name = POWER_PELLET
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50
        self.flashTime = 0.2
        self.timer = 0

    def update(self, dt):
        """
        This is mainly for showing off the flashing animation on screen.
        :param dt: time elapsed since the last flash
        :return: None
        """
        self.timer += dt
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0


class PelletGroup(object):
    """
    Object class to represent a group of pellets.
    """
    def __init__(self, pellet_file):
        self.pellet_list = []
        self.power_pellets = []
        self.create_pellet_list(pellet_file)
        self.num_eaten = 0

    def update(self, dt):
        for power_pellet in self.power_pellets:
            power_pellet.update(dt)

    def create_pellet_list(self, pellet_file):
        """
        Reads a maze text file for any keys matching those of pellets and creates a list.
        :param pellet_file: text file that contains pellets to eat
        :return: None
        """
        data = self.read_pellet_file(pellet_file)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in ['.', '+']:
                    self.pellet_list.append(Pellet(row, col))
                elif data[row][col] in ['P', 'p']:
                    pp = PowerPellet(row, col)
                    self.pellet_list.append(pp)
                    self.power_pellets.append(pp)

    @staticmethod
    def read_pellet_file(textfile):
        """
        Reads a text file for any keys matching those of pellets.
        :param textfile: text file that contains pellets to eat
        :return: readable data from textfile
        """
        return np.loadtxt(textfile, dtype='<U1')

    def is_empty(self):
        """Is the pellets list empty?"""
        if len(self.pellet_list) == 0:
            return True
        return False

    def render(self, screen):
        for pellet in self.pellet_list:
            pellet.render(screen)
