from constants import *

class MainMode(object):
    """
    This class represents the main modes for the ghost's movements.
    """

    def __init__(self):
        self.time = None
        self.mode = None
        self.timer = 0
        self.scatter()

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.time:
            if self.mode is SCATTER:
                self.chase()
            elif self.mode is CHASE:
                self.scatter()

    def scatter(self):
        """
        This mode tells the ghosts to scatter to one of the four corners of the maze.
        Each ghost has their own corner: Blinky goes top right, Inky goes bottom right,
        Pinky goes top left, and Clyde goes bottom left.
        """
        self.mode = SCATTER
        self.time = 7
        self.timer = 0

    def chase(self):
        """
        This, like the scatter mode, is different for all the ghosts:

        Blinky will always follow pacman, but unlike the other ghosts, he has a special mode
        where once pacman eats a certain amount of pellets, he enters a "Cruise Elroy" or "Angry" phase in which
        his speed will match that of pacman, making it nigh impossible to avoid him
        (The amount of pellets required to be eaten decreases from 224 at level 1 at different rates).

        Pinky's target is always four spaces (2 pellets) ahead of pacman's current position,
        mainly trying to trap the player, either for her to get to him, or allowing one of the other
        ghosts to come from behind.

        Inky's movement target is the most complex of the four. It is not only based on pacman's
        direction AND position, but also Blinky's. He will target a space in front of pacman, but will
        then move to a space twice the distance from Blinky's current position. While this may seem
        erratic, it's what makes him a formidable foe when teamed up with Blinky.

        Clyde's movement is all about proximity. If he is outside of pacman's range within an 8-pellet
        radius, he will chase pacman like Blinky, but once he's in that circle, he will switch to his
        scatter mode and evade pacman down to the bottom-left corner. This odd, cowardly
        movement choice is why he's often labeled as "the dumb one."
        """
        self.mode = CHASE
        self.time = 20
        self.timer = 0

class ModeController(object):
    """
    This class allows the ghosts to switch between different ghost modes.
    """
    def __init__(self, entity):
        self.timer = 0
        self.time = None
        self.main_mode = MainMode()
        self.current = self.main_mode.mode
        self.entity = entity

    def update(self, dt):
        self.main_mode.update(dt)
        if self.current is FREIGHT:
            self.timer += dt
            if self.timer >= self.time:
                self.time = None
                self.entity.normal_mode()
                self.current = self.main_mode.mode
        elif self.current in [SCATTER, CHASE]:
            self.current = self.main_mode.mode
        if self.current is SPAWN:
            if self.entity.node == self.entity.spawn_node:
                self.entity.normal_mode()
                self.current = self.main_mode.mode

    def set_spawn_mode(self):
        if self.current is FREIGHT:
            self.current = SPAWN

    def set_freight_mode(self):
        fright_time = get_level_spec(self.entity.level)["fright_time"]
        if fright_time <= 0:
            return
        if self.current in [SCATTER, CHASE]:
            self.timer = 0
            self.time = fright_time
            self.current = FREIGHT
        elif self.current is FREIGHT:
            self.timer = 0
