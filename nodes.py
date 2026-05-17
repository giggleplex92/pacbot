import numpy as np
import pygame

from constants import *
from vector import Vector


class Node(object):
    """
    Defines a singular node. These nodes and the connections between them are the
    main points in which both pacman and the ghosts can move through.
    """
    def __init__(self, x, y):
        self.position = Vector(x, y)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL: None}
        self.access = {UP: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       DOWN: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       LEFT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       RIGHT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT]}

    def render(self, screen):
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.as_tuple()
                line_end = self.neighbors[n].position.as_tuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.as_int(), 12)

    def deny_access(self, direction, entity):
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allow_access(self, direction, entity):
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)


class NodeGroup(object):
    """
    Object class that defines a group of nodes.
    """
    def __init__(self, level):
        self.level = level
        self.nodesLUT = {}
        self.nodeSymbols = ['+', 'P', 'n']
        self.pathSymbols = ['.', '-', '|', 'p']
        data = self.read_maze_file(level)
        self.create_node_table(data)
        self.connect_horizontally(data)
        self.connect_vertically(data)
        self.home_key = None

    def render(self, screen):
        for node in self.nodesLUT.values():
            node.render(screen)

    @staticmethod
    def read_maze_file(textfile):
        """Returns computer-readable data of a maze file."""
        return np.loadtxt(textfile, dtype='<U1')

    def create_node_table(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.construct_key(col + xoffset, row + yoffset)
                    self.nodesLUT[(x, y)] = Node(x, y)

    @staticmethod
    def construct_key(x, y):
        return x * TILEWIDTH, y * TILEHEIGHT

    def connect_horizontally(self, data, xoffset=0, yoffset=0):
        """
        Connects nodes horizontally, if applicable.
        """
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.construct_key(col + xoffset, row + yoffset)
                    else:
                        other_key = self.construct_key(col + xoffset, row + yoffset)
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[other_key]
                        self.nodesLUT[other_key].neighbors[LEFT] = self.nodesLUT[key]
                        key = other_key
                elif data[row][col] not in self.pathSymbols:
                    key = None

    def connect_vertically(self, data, xoffset=0, yoffset=0):
        """Connects nodes vertically, if applicable."""
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.construct_key(col + xoffset, row + yoffset)
                    else:
                        other_key = self.construct_key(col + xoffset, row + yoffset)
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[other_key]
                        self.nodesLUT[other_key].neighbors[UP] = self.nodesLUT[key]
                        key = other_key
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

    def get_node_from_pixels(self, x_pixel, y_pixel):
        if (x_pixel, y_pixel) in self.nodesLUT.keys():
            return self.nodesLUT[(x_pixel, y_pixel)]
        return None

    def get_node_from_tiles(self, col, row):
        x, y = self.construct_key(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None

    def get_start_temp_node(self):
        nodes = list(self.nodesLUT.values())
        return nodes[0]

    def set_portal_pair(self, pair1, pair2):
        """
        Makes the provided pair of nodes a pair of portals, mainly to give the
        illusion that pacman is traveling across one side of the screen to the other.
        """
        key1 = self.construct_key(*pair1)
        key2 = self.construct_key(*pair2)
        if key1 in self.nodesLUT.keys() and key2 in self.nodesLUT.keys():
            self.nodesLUT[key1].neighbors[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbors[PORTAL] = self.nodesLUT[key1]

    def create_home_nodes(self, xoffset, yoffset):
        home_data = np.array([['X', 'X', '+', 'X', 'X'],
                              ['X', 'X', '.', 'X', 'X'],
                              ['+', 'X', '.', 'X', '+'],
                              ['+', '.', '+', '.', '+'],
                              ['+', 'X', 'X', 'X', '+']])

        self.create_node_table(home_data, xoffset, yoffset)
        self.connect_horizontally(home_data, xoffset, yoffset)
        self.connect_vertically(home_data, xoffset, yoffset)
        self.home_key = self.construct_key(xoffset + 2, yoffset)
        return self.home_key

    def connect_home_nodes(self, home_key, other_key, direction):
        key = self.construct_key(*other_key)
        self.nodesLUT[home_key].neighbors[direction] = self.nodesLUT[key]
        self.nodesLUT[key].neighbors[direction * -1] = self.nodesLUT[home_key]

    def deny_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.deny_access(direction, entity)

    def allow_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.allow_access(direction, entity)

    def deny_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.deny_access(col, row, direction, entity)

    def allow_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.allow_access(col, row, direction, entity)

    def deny_home_access(self, entity):
        self.nodesLUT[self.home_key].deny_access(DOWN, entity)

    def allow_home_access(self, entity):
        self.nodesLUT[self.home_key].allow_access(DOWN, entity)

    def deny_home_access_list(self, entities):
        for entity in entities:
            self.deny_home_access(entity)

    def allow_home_access_list(self, entities):
        for entity in entities:
            self.allow_home_access(entity)