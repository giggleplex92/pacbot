# Background of game
TILEWIDTH = 16
TILEHEIGHT = 16
NROWS = 36
NCOLS = 28
SCREENWIDTH = NCOLS * TILEWIDTH
SCREENHEIGHT = NROWS * TILEHEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)
BLACK = (0, 0, 0)

# Pacman
YELLOW = (255, 255, 0)

STOP = 0
UP = 1
DOWN = -1
LEFT = 2
RIGHT = -2

PACMAN = 0
PELLET = 1
POWER_PELLET = 2

#Ghosts
GHOST = 3

"""
The following four constants are for each of the ghost modes.

SCATTER: This mode tells the ghosts to scatter to one of the four corners of the maze. 
Each ghost has their own corner: Blinky goes top right, Inky goes bottom right,
Pinky goes top left, and Clyde goes bottom left.

CHASE: This, like the scatter mode, is different for all of the ghosts:

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

FREIGHT: What the ghosts do when pacman has eaten a power pellet. They will move randomly
and at a slower speed. The time of this mode decreases as pacman progresses.

SPAWN: Behavior after a ghost has been eaten. They will move to the ghost house (center box)
to respawn, and will move at a much faster pace. After a few seconds, they will then respawn and
change modes.

SCATTER and CHASE are the main modes that the ghosts will use, and they can change them
at certain intervals. FREIGHT and SPAWN are interrupt modes, and are only done once pacman
interacts with them via eating them.
"""
SCATTER = 0
CHASE = 1
FREIGHT = 2
SPAWN = 3

FREIGHT_ANIM = 3

PINK = (255,183,150)
TEAL = (1,255,255)
ORANGE = (255,183,81)

BLINKY = 4
PINKY = 5
INKY = 6
CLYDE = 7


# Nodes
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PORTAL = 3

#Fruit
GREEN = (0, 255, 0)
FRUIT = 8
FRUIT_NAMES = ("CHERRY", "STRAWBERRY", "PEACH", "APPLE", "GRAPES", "GALAXIAN", "BELL", "KEY")
FRUIT_POINTS = {"CHERRY": 100, "STRAWBERRY": 300, "PEACH": 500, "APPLE": 700, "GRAPES": 1000, "GALAXIAN": 2000, "BELL": 3000, "KEY": 5000}
FRUIT_SPRITES = {"CHERRY": (2, 3), "STRAWBERRY": (3, 3), "PEACH": (4, 3), "APPLE": (5, 3), "GRAPES": (6, 3), "GALAXIAN": (7,3), "BELL": (8,3), "KEY": (9,3)}

# Level speeds from The Pac-Man Dossier, Table A.1.
BASE_SPEED = 75.75757625
PACMAN_SPEED = 150
GHOST_SPEED = 125
FRIGHT_GHOST_SPEED = 75
SPAWN_SPEED = 250

LEVEL_SPECS = (
    {"pacman": .80, "pacman_dots": .71, "ghost": .75, "ghost_tunnel": .40, "elroy1_dots": 20, "elroy1": .80, "elroy2_dots": 10, "elroy2": .85, "fright_pacman": .90, "fright_pacman_dots": .79, "fright_ghost": .50, "fright_time": 6, "fright_flashes": 5},
    {"pacman": .90, "pacman_dots": .79, "ghost": .85, "ghost_tunnel": .45, "elroy1_dots": 30, "elroy1": .90, "elroy2_dots": 15, "elroy2": .95, "fright_pacman": .95, "fright_pacman_dots": .83, "fright_ghost": .55, "fright_time": 5, "fright_flashes": 5},
    {"pacman": .90, "pacman_dots": .79, "ghost": .85, "ghost_tunnel": .45, "elroy1_dots": 40, "elroy1": .90, "elroy2_dots": 20, "elroy2": .95, "fright_pacman": .95, "fright_pacman_dots": .83, "fright_ghost": .55, "fright_time": 4, "fright_flashes": 5},
    {"pacman": .90, "pacman_dots": .79, "ghost": .85, "ghost_tunnel": .45, "elroy1_dots": 40, "elroy1": .90, "elroy2_dots": 20, "elroy2": .95, "fright_pacman": .95, "fright_pacman_dots": .83, "fright_ghost": .55, "fright_time": 3, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 40, "elroy1": 1.00, "elroy2_dots": 20, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 2, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 50, "elroy1": 1.00, "elroy2_dots": 25, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 5, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 50, "elroy1": 1.00, "elroy2_dots": 25, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 2, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 50, "elroy1": 1.00, "elroy2_dots": 25, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 2, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 60, "elroy1": 1.00, "elroy2_dots": 30, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 1, "fright_flashes": 3},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 60, "elroy1": 1.00, "elroy2_dots": 30, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 5, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 60, "elroy1": 1.00, "elroy2_dots": 30, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 2, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 80, "elroy1": 1.00, "elroy2_dots": 40, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 1, "fright_flashes": 3},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 80, "elroy1": 1.00, "elroy2_dots": 40, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 1, "fright_flashes": 3},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 80, "elroy1": 1.00, "elroy2_dots": 40, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 3, "fright_flashes": 5},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 100, "elroy1": 1.00, "elroy2_dots": 50, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 1, "fright_flashes": 3},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 100, "elroy1": 1.00, "elroy2_dots": 50, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 1, "fright_flashes": 3},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 100, "elroy1": 1.00, "elroy2_dots": 50, "elroy2": 1.05, "fright_pacman": None, "fright_pacman_dots": None, "fright_ghost": None, "fright_time": 0, "fright_flashes": 0},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 100, "elroy1": 1.00, "elroy2_dots": 50, "elroy2": 1.05, "fright_pacman": 1.00, "fright_pacman_dots": .87, "fright_ghost": .60, "fright_time": 1, "fright_flashes": 3},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 120, "elroy1": 1.00, "elroy2_dots": 60, "elroy2": 1.05, "fright_pacman": None, "fright_pacman_dots": None, "fright_ghost": None, "fright_time": 0, "fright_flashes": 0},
    {"pacman": 1.00, "pacman_dots": .87, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 120, "elroy1": 1.00, "elroy2_dots": 60, "elroy2": 1.05, "fright_pacman": None, "fright_pacman_dots": None, "fright_ghost": None, "fright_time": 0, "fright_flashes": 0},
    {"pacman": .90, "pacman_dots": .79, "ghost": .95, "ghost_tunnel": .50, "elroy1_dots": 120, "elroy1": 1.00, "elroy2_dots": 60, "elroy2": 1.05, "fright_pacman": None, "fright_pacman_dots": None, "fright_ghost": None, "fright_time": 0, "fright_flashes": 0},
)

def get_level_spec(level):
    return LEVEL_SPECS[min(level, len(LEVEL_SPECS) - 1)]

def level_speed(level, key):
    spec = get_level_spec(level)
    if key in ("pacman", "fright_pacman"):
        return PACMAN_SPEED
    if key == "ghost":
        return GHOST_SPEED
    if key == "fright_ghost":
        return FRIGHT_GHOST_SPEED
    if key == "elroy1":
        return PACMAN_SPEED
    if key == "elroy2":
        return PACMAN_SPEED * spec["elroy2"] / spec["elroy1"]
    if key == "pacman_dots":
        return PACMAN_SPEED * spec["pacman_dots"] / spec["pacman"]
    if key == "ghost_tunnel":
        return GHOST_SPEED * spec["ghost_tunnel"] / spec["ghost"]
    return BASE_SPEED * spec[key]

#Text
SCORETXT = 0
LEVELTXT = 1
READYTXT = 2
PAUSETXT = 3
GAMEOVERTXT = 4
HIGHSCORETXT = 5