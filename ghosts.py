from vector import Vector
from constants import *
from entity import Entity
from modes import ModeController
from sprites import GhostSprites


class Ghost(Entity):
    """
    This class represents a ghost. Each one will have their own separate movements,
    but this class will represent them as a whole. If pacman collides with a ghost,
    and unless he is under the effects of a power pellet, he will die, and lose a life.
    If all lives are lost, it's game over.
    """

    ghost_name = GHOST
    ghost_color = WHITE

    def __init__(self, node, pacman = None, blinky = None, level=0):
        Entity.__init__(self, node)
        self.level = level
        self.spawn_node = None
        self.name = self.ghost_name
        self.points = 200
        self.goal = Vector()
        self.direction_method = self.goal_direction
        self.pacman = pacman
        self.mode = ModeController(self)
        self.blinky = blinky
        self.home_node = node
        self.color = self.ghost_color
        self.set_speed(level_speed(self.level, "ghost"))
        self.sprites = GhostSprites(self)


    def update(self, dt):
        self.sprites.update(dt)
        self.mode.update(dt)
        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()
        Entity.update(self, dt)

    def scatter(self):
        self.goal = Vector()

    def chase(self):
        self.goal = self.pacman.position

    def start_freight(self):
        self.mode.set_freight_mode()
        if self.mode.current == FREIGHT:
            self.set_speed(level_speed(self.level, "fright_ghost"))
            self.direction_method = self.random_direction

    def normal_mode(self):
        self.set_speed(level_speed(self.level, "ghost"))
        self.direction_method = self.goal_direction
        self.home_node.deny_access(DOWN, self)

    def spawn(self):
        self.goal = self.spawn_node.position

    def set_spawn_node(self, node):
        self.spawn_node = node

    def start_spawn(self):
        self.mode.set_spawn_mode()
        if self.mode.current == SPAWN:
            self.set_speed(SPAWN_SPEED)
            self.direction_method = self.goal_direction
            self.spawn()

    def reset(self):
        Entity.reset(self)
        self.points = 200
        self.direction_method = self.goal_direction


class Blinky(Ghost):
    """
    This class represents Blinky (or Shadow), the de facto leader of the ghosts.
    In scatter mode, he patrols the top-left corner. In chase mode, his movement pattern
    is simple: Just follow pacman. However, eat too many pellets, and he goes into a special
    "Angry" state (Some call this his "Cruise Elroy" state). Either way, his speed will increase
    to match that of pacman's, and the amount of pellets required to activate this mode will
    decrease as the player progresses, so stay on your toes around him!
    """
    ghost_name = BLINKY
    ghost_color = RED

    def __init__(self, node, pacman = None, blinky = None, level=0):
        Ghost.__init__(self, node, pacman, blinky, level)
        self.elroy_stage = 0

    def scatter(self):
        if self.elroy_stage:
            self.chase()
        else:
            self.goal = Vector(TILEWIDTH*NCOLS, 0)

    def enter_cruise(self, stage=1):
        """Once pacman eats enough pellets, activate Blinky's "Cruise Elroy" state,
        where his speed will match that of pacman's. This speed boost will reset upon either
        completing a level, or losing all your lives."""
        if self.mode.current != SPAWN and stage > self.elroy_stage:
            self.elroy_stage = stage
            if self.mode.current != FREIGHT:
                self.set_speed(self.elroy_speed())

    def elroy_speed(self):
        if self.elroy_stage >= 2:
            return level_speed(self.level, "elroy2")
        return level_speed(self.level, "elroy1")

    def normal_mode(self):
        Ghost.normal_mode(self)
        if self.elroy_stage:
            self.set_speed(self.elroy_speed())

    def reset(self):
        Entity.reset(self)
        self.elroy_stage = 0
        self.set_speed(level_speed(self.level, "ghost"))

class Pinky(Ghost):
    """
    Pinky, the only female member of the crew, also has a crush on pacman. Of course,
    this translates into her chase movement pattern with her always trying to be 4 steps (or spaces)
    ahead of pacman. Combined with Blinky, they'll try to sandwich you and end your run,
    so it's best to, ironically, ghost her. She always retreats to the top left during scatter,
    and she doesn't have any unique abilities like Blinky. She was originally called "Speedy."
    """
    ghost_name = PINKY
    ghost_color = PINK

    def __init__(self, node, pacman=None, blinky=None, level=0):
        Ghost.__init__(self, node, pacman, blinky, level)

    def chase(self):
        self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4

class Inky(Ghost):
    """
    Inky, once called "Bashful," has the most complex chase movement patterns of all 4 of the
    ghosts, requiring the knowledge of both Blinky's and Pacman's positions. To start, find
    the position 2 spaces ahead of pacman, then subtract that from Blinky's position,
    and then multiply the result by 2. Finally, add the result to Blinky's position to
    get Inky's position. Like Pinky, this complicated movement may also result in a sandwich
    with Blinky, albeit a little more often than Pinky. His scatter goal is the bottom right corner.
    """
    ghost_name = INKY
    ghost_color = TEAL

    def __init__(self, node, pacman=None, blinky=None, level=0):
        Ghost.__init__(self, node, pacman, blinky, level)

    def scatter(self):
        self.goal = Vector(TILEWIDTH*NCOLS, TILEHEIGHT*NROWS)

    def chase(self):
        vec1 = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 2
        vec2 = (vec1 - self.blinky.position) * 2
        self.goal = self.blinky.position + vec2

class Clyde(Ghost):
    """
    The dumb one of the group and originally called "Pokey," Clyde always moves to the bottom left
    in scatter mode. In chase mode, he moves based on his proximity to pacman's position, going to his
    scatter location when he is within an 8-tile radius between himself and pacman,
    and then going to chase pacman once out of that range.
    """

    ghost_name = CLYDE
    ghost_color = ORANGE

    def __init__(self, node, pacman=None, blinky=None, level=0):
        Ghost.__init__(self, node, pacman, blinky, level)

    def scatter(self):
        self.goal = Vector(0, TILEHEIGHT * NROWS)

    def chase(self):
        d = self.pacman.position - self.position
        ds = d.magnitude_squared()
        if ds <= (TILEWIDTH * 8) ** 2:
            self.scatter()
        else:
            self.goal = self.pacman.position

class GhostGroup(object):
    def __init__(self, node, pacman, level=0):
        self.blinky = Blinky(node, pacman, level=level)
        self.pinky = Pinky(node, pacman, level=level)
        self.inky = Inky(node, pacman, self.blinky, level=level)
        self.clyde = Clyde(node, pacman, level=level)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

    def __iter__(self):
        return iter(self.ghosts)

    def update(self, dt):
        for ghost in self:
            ghost.update(dt)

    def start_freight(self):
        for ghost in self:
            ghost.start_freight()
        self.reset_points()

    def set_spawn_node(self, node):
        for ghost in self:
            ghost.set_spawn_node(node)

    def update_points(self):
        for ghost in self:
            ghost.points *= 2

    def reset_points(self):
        for ghost in self:
            ghost.points = 200

    def reset(self):
        for ghost in self:
            ghost.reset()

    def hide(self):
        for ghost in self:
            ghost.visible = False

    def show(self):
        for ghost in self:
            ghost.visible = True

    def render(self, screen):
        for ghost in self:
            ghost.render(screen)
