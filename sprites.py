import pygame
from pygame import Color

from constants import *
import numpy as np
from animation import Animator

BASETILEWIDTH = 16
BASETILEHEIGHT = 16

DEATH = 5


class Spritesheet(object):
    def __init__(self):
        if not hasattr(self, "file_name"):
            self.file_name = "Pac-Man_Comparable_Sprite_Sheet.bmp"
        self.load_sheet(self.file_name)
        if not hasattr(self, "transparent_color"):
            self.transparent_color = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(self.transparent_color)
        width = int(self.sheet.get_width() / BASETILEWIDTH * TILEWIDTH)  # = 1
        height = int(self.sheet.get_height() / BASETILEHEIGHT * TILEHEIGHT)  # = 1
        self.sheet = pygame.transform.scale(self.sheet, (width, height))
        self.sheet.set_colorkey(self.transparent_color)

    def get_image(self, x, y, width=None, height=None):
        if width is None:
            width = TILEWIDTH
        if height is None:
            height = TILEHEIGHT
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return pygame.transform.scale(self.sheet.subsurface(self.sheet.get_clip()).convert(), (32, 32))

    def load_sheet(self, file_name):
        self.sheet = pygame.image.load(file_name).convert()

class PacmanSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)
        self.entity = entity
        self.entity.image = self.get_start_image()
        self.animations = {}
        self.define_animations()
        self.stop_image = (2, 0)

    def get_start_image(self):
        return self.get_image(1, 1)

    def get_image(self, x, y, width=None, height=None):
        return Spritesheet.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)

    def define_animations(self):
        self.animations[LEFT] = Animator(((2, 0), (1, 1), (0, 1), (1, 1)))
        self.animations[RIGHT] = Animator(((2, 0), (1, 0), (0, 0), (1, 0)))
        self.animations[UP] = Animator(((2, 0), (1, 2), (0, 2), (1, 2)))
        self.animations[DOWN] = Animator(((2, 0), (1, 3), (0, 3), (1, 3)))
        self.animations[DEATH] = Animator(((3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10,0), (11,0), (12,0), (13,0), (13,1)), 6, False)

    def update(self, dt):
        if self.entity.alive:
            if self.entity.direction == LEFT:
                self.entity.image = self.get_image(*self.animations[LEFT].update(dt))
                self.stop_image = (2, 0)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.get_image(*self.animations[RIGHT].update(dt))
                self.stop_image = (2, 0)
            elif self.entity.direction == DOWN:
                self.entity.image = self.get_image(*self.animations[DOWN].update(dt))
                self.stop_image = (2, 0)
            elif self.entity.direction == UP:
                self.entity.image = self.get_image(*self.animations[UP].update(dt))
                self.stop_image = (2, 0)
            elif self.entity.direction == STOP:
                self.entity.image = self.get_image(*self.stop_image)
        else:
            self.entity.image = self.get_image(*self.animations[DEATH].update(dt))

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class GhostSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)
        self.animations = {}
        self.y = {BLINKY: 4, PINKY: 5, INKY: 6, CLYDE: 7}
        self.entity = entity
        self.stop_image = (2, self.y[self.entity.name])
        self.define_animations()
        self.entity.image = self.get_start_image()

    def get_start_image(self):
        return self.get_image(2, self.y[self.entity.name])

    def get_image(self, x, y, width=None, height=None):
        return Spritesheet.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)

    def define_animations(self):
        y = self.y[self.entity.name]
        self.animations[LEFT] = Animator(((2, y), (3, y)))
        self.animations[RIGHT] = Animator(((0, y), (1, y)))
        self.animations[UP] = Animator(((4, y), (5, y)))
        self.animations[DOWN] = Animator(((6, y), (7, y)))
        self.animations[FREIGHT_ANIM] = Animator(((8, 4), (9, 4)), 5)


    def update(self, dt):
        y = self.y[self.entity.name]
        if self.entity.mode.current in [SCATTER, CHASE]:
            if self.entity.direction == LEFT:
                self.entity.image = self.get_image(*self.animations[LEFT].update(dt))
                self.stop_image = (2, y)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.get_image(*self.animations[RIGHT].update(dt))
                self.stop_image = (2, y)
            elif self.entity.direction == DOWN:
                self.entity.image = self.get_image(*self.animations[DOWN].update(dt))
                self.stop_image = (2, y)
            elif self.entity.direction == UP:
                self.entity.image = self.get_image(*self.animations[UP].update(dt))
                self.stop_image = (2, y)
            elif self.entity.direction == STOP:
                self.entity.image = self.get_image(*self.stop_image)
        elif self.entity.mode.current == FREIGHT:
            self.entity.image = self.get_image(*self.get_freight_frame(dt))
        elif self.entity.mode.current == SPAWN:
            if self.entity.direction == LEFT:
                self.entity.image = self.get_image(9, 5)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.get_image(8, 5)
            elif self.entity.direction == DOWN:
                self.entity.image = self.get_image(11, 5)
            elif self.entity.direction == UP:
                self.entity.image = self.get_image(10, 5)
            elif self.entity.direction == STOP:
                self.entity.image = self.get_image(8, 5)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()
        self.stop_image = (2, self.y[self.entity.name])
        self.entity.image = self.get_start_image()

    def get_freight_frame(self, dt):
        mode = self.entity.mode
        spec = get_level_spec(self.entity.level)
        flash_count = spec["fright_flashes"]
        if not mode.time or flash_count <= 0:
            return self.animations[FREIGHT_ANIM].update(dt)

        flash_duration = min(mode.time, flash_count * 0.5)
        time_left = mode.time - mode.timer
        if time_left > flash_duration:
            return self.animations[FREIGHT_ANIM].update(dt)

        flash_index = int((flash_duration - time_left) * 4)
        if flash_index % 2 == 0:
            return (10, 4) if flash_index % 4 == 0 else (11, 4)
        return self.animations[FREIGHT_ANIM].update(dt)

class FruitSprites(Spritesheet):
    def __init__(self, entity=None, fruit_name="CHERRY"):
        Spritesheet.__init__(self)
        self.entity = entity
        if self.entity is not None:
            self.entity.image = self.get_start_image(fruit_name)

    def get_start_image(self, fruit_name):
        return self.get_fruit_image(fruit_name)

    def get_fruit_image(self, fruit_name):
        return self.get_image(*FRUIT_SPRITES[fruit_name])

    def get_image(self, x, y, width=None, height=None):
        return Spritesheet.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)

class LifeSprites(Spritesheet):
    def __init__(self, num_lives):
        Spritesheet.__init__(self)
        self.images = None
        self.reset_lives(num_lives)

    def remove_image(self):
        if len(self.images) > 0:
            self.images.pop(0)

    def reset_lives(self, num_lives):
        self.images = []
        for i in range(num_lives):
            self.images.append(self.get_image(8, 1))

    def get_image(self, x, y, width=None, height=None):
        return Spritesheet.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)

class MazeSprites(Spritesheet):
    def __init__(self, maze_file, rotation_file):
        self.file_name = "spritesheet.bmp"
        self.transparent_color = Color(255, 0, 255)
        Spritesheet.__init__(self)
        self.data = self.read_maze_file(maze_file)
        self.rotation_data = self.read_maze_file(rotation_file)

    def get_image(self, x, y, width=None, height=None):
        if width is None:
            width = TILEWIDTH
        if height is None:
            height = TILEHEIGHT
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        sprite = self.sheet.subsurface(self.sheet.get_clip()).copy()
        sprite.set_colorkey(self.transparent_color)
        return sprite

    @staticmethod
    def read_maze_file(maze_file):
        return np.loadtxt(maze_file, dtype='<U1')

    def construct_background(self, background, y):
        for row in list(range(self.data.shape[0])):
            for col in list(range(self.data.shape[1])):
                if self.data[row][col].isdigit():
                    x = int(self.data[row][col]) + 12
                    sprite = self.get_image(x, y)
                    rotation = self.rotation_data[row][col]
                    rotation_val = int(rotation) if rotation.isdigit() else 0
                    sprite = self.rotate(sprite, rotation_val)
                    background.blit(sprite, (col * TILEWIDTH, row * TILEHEIGHT))
                elif self.data[row][col] == '=':
                    sprite = self.get_image(10, 8, TILEWIDTH, TILEHEIGHT)
                    background.blit(sprite, (col * TILEWIDTH, row * TILEHEIGHT))

        return background

    def rotate(self, sprite, value):
        sprite = pygame.transform.rotate(sprite, value * 90)
        sprite.set_colorkey(self.transparent_color)
        return sprite

if __name__ == "__main__":
    test_screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
    spritesheet_test = Spritesheet()
    image = spritesheet_test.get_image(1, 1, 16, 16)
    pygame.transform.scale(image, (32, 32))
    pygame.image.save(image, "pacman_tile.bmp")
