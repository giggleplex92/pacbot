from entity import Entity
from constants import *
from sprites import FruitSprites


def get_name_for_level(level):
    return FRUIT_NAMES[min(level, len(FRUIT_NAMES) - 1)]


class Fruit(Entity):
    """
    This class represents fruit, an item in pacman that gives him big points when eaten. There are
    8 fruit objects in total, each awarding a different amount of points.

    Cherry: 100 points \n
    Strawberry: 300 points \n
    Peach: 500 points \n
    Apple: 700 points \n
    Grapes: 1,000 points \n
    Galaxian: 2,000 points \n
    Bell: 3,000 points \n
    Key: 5,000 points \n

    2 fruits can be given per maze: 1 after eating 70 pellets, and another after 100 more.
    The first fruit will be replaced if not eaten by the time the 2nd fruit appears.
    Better be quick, though, as they will disappear after 9-10 seconds have elapsed!

    Fun fact: The Galaxian is a reference to galaga, another Bandai-Namco arcade game.
    """
    def __init__(self, node, level=0):
        Entity.__init__(self, node)
        self.name = get_name_for_level(level)
        self.color = GREEN
        self.lifespan = 5
        self.timer = 0
        self.destroy = False
        self.points = FRUIT_POINTS[self.name]
        self.set_between_nodes(RIGHT)
        self.sprites = FruitSprites(self, self.name)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True
