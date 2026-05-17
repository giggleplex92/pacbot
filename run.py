import pygame
import os
import sys
from pygame.locals import *
from constants import *
from nodes import NodeGroup
from pacman import Pacman
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from sprites import LifeSprites, MazeSprites, FruitSprites
from maze_data import MazeData
from text import TextGroup, Text
import numpy as np


class GameController(object):
    """
    Main class to run the game, render it, and allows user control via keyboard input.
    """

    def __init__(self, render_enabled=True, sound_enabled=True):
        self.title_text = None
        self.title_screen = None
        self.screen_state = "title"
        self.render_enabled = render_enabled
        self.sound_enabled = sound_enabled
        self.maze_sprites = None
        self.ghosts = None
        self.pellets = None
        self.nodes = None
        self.pacman = None
        self.fruit_captured = []
        self.game_mode = "ai"
        self.ai_model = None
        self.ai_model_load_attempted = False
        self.ai_status_message = "Loading saved DQN agent..."
        self.ai_countdown_time = 5.0

        # PRE-INIT: Ensures clean audio buffers
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)
        pygame.mixer.set_reserved(2)

        self.screen = pygame.display.set_mode(SCREENSIZE if self.render_enabled else (1, 1), 0, 32)

        # Load one-shot sounds
        self.snd_eat_dot = [pygame.mixer.Sound("Sounds/eat_dot_0.wav"), pygame.mixer.Sound("Sounds/eat_dot_1.wav")]
        self.eat_dot_toggle = 0
        self.snd_eat_fruit = pygame.mixer.Sound("Sounds/eat_fruit.wav")
        self.snd_eat_ghost = pygame.mixer.Sound("Sounds/eat_ghost.wav")
        self.snd_extend = pygame.mixer.Sound("Sounds/extend.wav")
        self.snd_fail = pygame.mixer.Sound("Sounds/15. Fail.mp3")
        self.snd_start = pygame.mixer.Sound("Sounds/start.wav")

        # Load looping ambient sounds
        self.snd_power = pygame.mixer.Sound("Sounds/12. Ghost - Turn to Blue.wav")
        self.snd_retreat = pygame.mixer.Sound("Sounds/14. Ghost - Return to Home.wav")

        # Load Ghost Siren sounds
        self.snd_siren_0 = pygame.mixer.Sound("Sounds/06. Ghost - Normal Move.wav")
        self.snd_siren_1 = pygame.mixer.Sound("Sounds/07. Ghost - Spurt Move 1.wav")
        self.snd_siren_2 = pygame.mixer.Sound("Sounds/08. Ghost - Spurt Move 2.wav")
        self.snd_siren_3 = pygame.mixer.Sound("Sounds/09. Ghost - Spurt Move 3.wav")
        self.snd_siren_4 = pygame.mixer.Sound("Sounds/10. Ghost - Spurt Move 4.wav")
        if not self.sound_enabled:
            for sound in [
                *self.snd_eat_dot,
                self.snd_eat_fruit,
                self.snd_eat_ghost,
                self.snd_extend,
                self.snd_fail,
                self.snd_start,
                self.snd_power,
                self.snd_retreat,
                self.snd_siren_0,
                self.snd_siren_1,
                self.snd_siren_2,
                self.snd_siren_3,
                self.snd_siren_4,
            ]:
                sound.set_volume(0)

        self.ambient_channel = pygame.mixer.Channel(0)
        self.death_channel = pygame.mixer.Channel(1)
        self.current_ambient = None

        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0

        # High Score variables
        self.high_score = self.load_high_score()
        self.high_score_beaten = False

        self.text_group = TextGroup()
        self.text_group.update_high_score(self.high_score)
        self.life_sprites = LifeSprites(self.lives)
        self.fruit_sprites = FruitSprites()
        self.flash_bg = False
        self.flash_time = 0.2
        self.flash_timer = 0
        self.maze_data = MazeData()

    @staticmethod
    def load_high_score():
        """Reads the high score from a local text file if it exists."""
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt", "r") as f:
                    return int(f.read())
            except ValueError:
                return 0
        return 0

    def save_high_score(self):
        """Saves the high score to a local text file."""
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except IOError:
            pass

    def restart_game(self):
        """Restart the game once all lives are lost."""
        self.lives = 5
        self.level = 0
        # self.pellets.num_eaten = 0
        self.pause.paused = True
        self.fruit = None
        self.score = 0
        self.high_score_beaten = False
        self.text_group.update_score(self.score)
        self.text_group.update_level(self.level)
        self.text_group.show_text(READYTXT)
        self.life_sprites.reset_lives(self.lives)
        self.fruit_captured.clear()
        self.ambient_channel.stop()
        self.load_title_screen()

    def restart_ai_game(self):
        """Restart AI play from level one without unloading the saved model."""
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.score = 0
        self.high_score_beaten = False
        self.text_group.update_score(self.score)
        self.text_group.update_level(self.level)
        self.life_sprites.reset_lives(self.lives)
        self.fruit_captured.clear()
        self.ambient_channel.stop()
        self.start_game("ai")

    def reset_level(self):
        """Reset the game level when a life is lost."""
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.text_group.show_text(READYTXT)
        self.ambient_channel.stop()
        self.show_entities()

        # Hard reset the pause state to false so set_pause guarantees a freeze
        self.pause.paused = False
        self.pause.set_pause(pause_time=2, func=self.text_group.hide_text)

    def set_background(self):
        """Initialize the game background"""
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.maze_sprites.construct_background(self.background_norm, self.level % 5)
        self.background_flash = self.maze_sprites.construct_background(self.background_flash, 5)
        self.flash_bg = False
        self.background = self.background_norm

    def start_game(self, game_mode=None):
        """Start the game"""
        if game_mode is not None:
            self.game_mode = game_mode
        self.title_screen = False
        self.screen_state = "game"
        self.maze_data.load_maze(self.level)
        self.maze_sprites = MazeSprites("Mazes/" + self.maze_data.obj.folder + "/" + self.maze_data.obj.name + ".txt",
                                        "Mazes/" + self.maze_data.obj.folder + "/" + self.maze_data.obj.name + "_rotation.txt")
        self.set_background()
        self.nodes = NodeGroup("Mazes/" + self.maze_data.obj.folder + "/" + self.maze_data.obj.name + ".txt")
        self.maze_data.obj.set_portal_pairs(self.nodes)
        self.maze_data.obj.connect_home_nodes(self.nodes)
        self.pacman = Pacman(self.nodes.get_node_from_tiles(*self.maze_data.obj.pacman_start), self.level)
        self.pacman.ai_mode = self.game_mode == "ai"
        self.pellets = PelletGroup("Mazes/" + self.maze_data.obj.folder + "/" + self.maze_data.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.get_start_temp_node(), self.pacman, self.level)
        self.ghosts.pinky.set_start_node(self.nodes.get_node_from_tiles(*self.maze_data.obj.add_offset(2, 3)))
        self.ghosts.inky.set_start_node(self.nodes.get_node_from_tiles(*self.maze_data.obj.add_offset(0, 3)))
        self.ghosts.clyde.set_start_node(self.nodes.get_node_from_tiles(*self.maze_data.obj.add_offset(4, 3)))
        self.ghosts.set_spawn_node(self.nodes.get_node_from_tiles(*self.maze_data.obj.add_offset(2, 3)))
        self.ghosts.blinky.set_start_node(self.nodes.get_node_from_tiles(*self.maze_data.obj.add_offset(2, 0)))
        self.nodes.deny_home_access(self.pacman)
        self.nodes.deny_home_access_list(self.ghosts)
        self.ghosts.inky.start_node.deny_access(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.start_node.deny_access(LEFT, self.ghosts.clyde)
        self.maze_data.obj.deny_ghosts_access(self.ghosts, self.nodes)

        self.hide_entities()
        self.text_group.show_text(READYTXT)
        self.ambient_channel.stop()
        self.current_ambient = None

        self.snd_start.play()

        # Hard reset the pause state to false so set_pause guarantees a freeze
        self.pause.paused = False
        self.pause.set_pause(pause_time=self.snd_start.get_length(), func=self.show_entities)

    def check_events(self):
        """Check for keyboard input and update the pellets and nodes"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.save_high_score()
                pygame.quit()  # Safely close the pygame window
                sys.exit()  # Safely terminate the Python script
            elif event.type == KEYDOWN:
                if not self.title_screen:
                    if event.key == K_SPACE:
                        if self.pacman.alive and self.pause.pause_time is None:
                            self.pause.set_pause(player_paused=True)
                            if not self.pause.paused:
                                self.text_group.hide_text()
                                self.show_entities()
                            else:
                                self.text_group.show_text(PAUSETXT)
                                self.hide_entities()
                else:
                    if self.screen_state == "title":
                        if event.key in (K_1, K_p):
                            self.load_controls_screen()
                        elif event.key in (K_2, K_a):
                            self.load_ai_info_screen()
                    elif self.screen_state == "controls":
                        if event.key == K_SPACE:
                            self.start_game("player")
                        elif event.key in (K_ESCAPE, K_BACKSPACE):
                            self.load_title_screen()
                    elif self.screen_state == "ai_info":
                        if event.key in (K_ESCAPE, K_BACKSPACE):
                            self.load_title_screen()

    def render(self):
        """Render the assets"""
        self.screen.blit(self.background, (0, 0))
        if not self.title_screen:
            self.pellets.render(self.screen)
            if self.fruit is not None:
                self.fruit.render(self.screen)
            self.pacman.render(self.screen)
            self.ghosts.render(self.screen)
            self.text_group.render(self.screen)

            for i in range(len(self.life_sprites.images)):
                x = self.life_sprites.images[i].get_width() * i
                y = SCREENHEIGHT - (self.life_sprites.images[i].get_height())
                self.screen.blit(self.life_sprites.images[i], (x, y))

            self.render_captured_fruits()
        else:
            self.render_title_screen()
        pygame.display.update()

    def render_title_screen(self):
        """Render menu, controls, and AI information screens."""
        if self.screen_state == "controls":
            lines = [
                ("CONTROLS", YELLOW, 24),
                ("ARROWS", WHITE, 12),
                ("MOVE PAC-MAN", WHITE, 12),
                ("SPACE", WHITE, 12),
                ("PAUSE / RESUME", WHITE, 12),
                ("YOU HAVE 5 LIVES", TEAL, 10),
                ("PRESS SPACE", YELLOW, 12),
                ("TO START", YELLOW, 12),
                ("ESC TO GO BACK", WHITE, 8),
            ]
            self.render_screen_lines(lines, start_y=56, gap=30)
        elif self.screen_state == "ai_info":
            countdown_value = max(1, int(self.ai_countdown_time + 0.999))
            lines = [
                ("AI MODE", YELLOW, 24),
                ("THE SAVED DQN AGENT", WHITE, 10),
                ("WILL PLAY PAC-MAN.", WHITE, 10),
                ("READ AI_PLAYER.PY", TEAL, 9),
                ("HOW THE AGENT WORKS.", TEAL, 9),
                ("FOR TRAINING GRAPHS,", WHITE, 9),
                ("RUN THIS COMMAND:", WHITE, 9),
                ("tensorboard --logdir", YELLOW, 8),
                ("pacman_tensorboard", YELLOW, 8),
                (self.ai_status_message, TEAL, 8),
                ("STARTING IN " + str(countdown_value) + "...", YELLOW, 12),
            ]
            self.render_screen_lines(lines, start_y=38, gap=28)
        else:
            lines = [
                ("PACMAN", YELLOW, 40),
                ("1  PLAYER", WHITE, 14),
                ("2  AI AGENT", WHITE, 14),
                ("P OR A ALSO WORK", TEAL, 8),
            ]
            self.render_screen_lines(lines, start_y=64, gap=54)

    def render_screen_lines(self, lines, start_y, gap):
        """Draw centered title-screen text without involving the in-game HUD."""
        y = start_y
        for text, color, size in lines:
            label = Text(text, color, 0, 0, size)
            label.position.x = (SCREENWIDTH - label.label.get_width()) / 2
            label.position.y = y
            label.render(self.screen)
            y += gap

    @staticmethod
    def get_fruit_name_for_level(level):
        return FRUIT_NAMES[min(level, len(FRUIT_NAMES) - 1)]

    def render_captured_fruits(self):
        fruit_names = self.fruit_captured[-len(FRUIT_NAMES):]
        if not fruit_names:
            return
        images = [self.fruit_sprites.get_fruit_image(name) for name in fruit_names]
        total_width = sum(image.get_width() for image in images)
        x = SCREENWIDTH - total_width
        y = SCREENHEIGHT - images[0].get_height()
        for image in images:
            self.screen.blit(image, (x, y))
            x += image.get_width()

    def manage_ambient_sounds(self):
        """Controls looping sounds based on Ghost Mode states and remaining pellets."""
        if self.title_screen or self.pause.paused or not self.pacman.alive:
            if self.current_ambient is not None:
                self.ambient_channel.stop()
                self.current_ambient = None
            return

        any_spawn = any(ghost.mode.current == SPAWN for ghost in self.ghosts)
        any_freight = any(ghost.mode.current == FREIGHT for ghost in self.ghosts)

        if any_spawn:
            target_sound = self.snd_retreat
        elif any_freight:
            target_sound = self.snd_power
        else:
            # Ghost movement speeds up visually and audibly based on pellets remaining!
            pellets_left = len(self.pellets.pellet_list)
            if pellets_left <= 30:
                target_sound = self.snd_siren_4
            elif pellets_left <= 60:
                target_sound = self.snd_siren_3
            elif pellets_left <= 120:
                target_sound = self.snd_siren_2
            elif pellets_left <= 180:
                target_sound = self.snd_siren_1
            else:
                target_sound = self.snd_siren_0

        if self.current_ambient != target_sound:
            self.ambient_channel.stop()
            self.current_ambient = target_sound
            if self.current_ambient is not None:
                self.ambient_channel.play(self.current_ambient, loops=-1)

    def update(self):
        """Update the assets that depend on time"""
        if self.render_enabled:
            dt = self.clock.tick(30) / 1000.0
        else:
            self.clock.tick(0)
            dt = 1 / 30.0
        if not self.title_screen:
            self.text_group.update(dt)
            if not self.pause.paused:
                self.pellets.update(dt)
                self.ghosts.update(dt)
                if self.fruit is not None:
                    self.fruit.update(dt)
                self.check_pellet_events()
                self.update_pacman_speed()
                self.check_ghost_events()
                self.check_fruit_events()
            if self.pacman.alive:
                if not self.pause.paused:
                    self.update_ai_agent_action()
                    self.pacman.update(dt)
            else:
                self.pacman.update(dt)

            if self.flash_bg:
                self.flash_timer += dt
                if self.flash_timer >= self.flash_time:
                    self.flash_timer = 0
                    if self.background == self.background_norm:
                        self.background = self.background_flash
                    else:
                        self.background = self.background_norm

            after_pause_method = self.pause.update(dt)
            if after_pause_method is not None:
                after_pause_method()
        else:
            self.update_title_screen(dt)

        if self.sound_enabled:
            self.manage_ambient_sounds()
        if self.render_enabled:
            self.check_events()
            self.render()

    def update_title_screen(self, dt):
        """Advance non-game title-screen states."""
        if self.screen_state == "ai_info":
            self.load_ai_model()
            self.ai_countdown_time -= dt
            if self.ai_countdown_time <= 0:
                self.start_game("ai")

    def load_ai_model(self):
        """Load the saved Stable-Baselines3 model only when AI mode is selected."""
        if self.ai_model_load_attempted:
            self.ai_status_message = "AGENT READY" if self.ai_model is not None else "AGENT LOAD FAILED"
            return
        self.ai_model_load_attempted = True
        try:
            from stable_baselines3 import DQN
            self.ai_model = DQN.load("pacman_dqn_agent")
            self.ai_status_message = "AGENT READY"
        except Exception as error:
            self.ai_model = None
            self.ai_status_message = "AGENT LOAD FAILED"
            print("Could not load pacman_dqn_agent.zip:", error)

    def update_ai_agent_action(self):
        """Ask the saved DQN model for Pac-Man's next direction during AI mode."""
        if self.game_mode != "ai" or self.ai_model is None or self.pacman is None:
            return
        action, _ = self.ai_model.predict(self.get_state(), deterministic=True)
        action_map = {0: UP, 1: DOWN, 2: LEFT, 3: RIGHT}
        self.pacman.ai_direction = action_map[int(np.asarray(action).item())]

    def update_score(self, points):
        self.score += points
        self.text_group.update_score(self.score)

        if self.score > self.high_score:
            if not self.high_score_beaten and self.high_score > 0:
                self.snd_extend.play()
                self.high_score_beaten = True
            self.high_score = self.score
            self.text_group.update_high_score(self.high_score)
            self.save_high_score()  # Saves dynamically as it updates

    def update_pacman_speed(self):
        if any(ghost.mode.current == FREIGHT for ghost in self.ghosts):
            self.pacman.set_speed(level_speed(self.level, "fright_pacman"))
        else:
            self.pacman.set_speed(level_speed(self.level, "pacman"))

    def check_fruit_events(self):
        if self.pellets.num_eaten == 70 or self.pellets.num_eaten == 170:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.get_node_from_tiles(*self.maze_data.obj.fruit_start), self.level)
        if self.fruit is not None:
            if self.pacman.collide_check(self.fruit):
                self.snd_eat_fruit.play()
                self.update_score(self.fruit.points)
                self.text_group.add_text(str(self.fruit.points), PINK, self.fruit.position.x, self.fruit.position.y, 8,
                                         time=1)
                self.fruit_captured.append(self.fruit.name)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def check_pellet_events(self):
        pellet = self.pacman.eat_pellets(self.pellets.pellet_list)
        if pellet:
            self.snd_eat_dot[self.eat_dot_toggle].play()
            self.eat_dot_toggle = 1 - self.eat_dot_toggle
            self.pellets.num_eaten += 1
            self.update_score(pellet.points)
            if self.pellets.num_eaten == 30:
                self.ghosts.inky.start_node.allow_access(RIGHT, self.ghosts.inky)
            if self.pellets.num_eaten == 70:
                self.ghosts.clyde.start_node.allow_access(LEFT, self.ghosts.clyde)

            pellets_left = len(self.pellets.pellet_list) - 1
            spec = get_level_spec(self.level)
            if pellets_left == spec["elroy1_dots"]:
                self.ghosts.blinky.enter_cruise(1)
            elif pellets_left == spec["elroy2_dots"]:
                self.ghosts.blinky.enter_cruise(2)

            self.pellets.pellet_list.remove(pellet)
            if pellet.name == POWER_PELLET:
                self.ghosts.start_freight()

            if self.pellets.is_empty():
                self.flash_bg = True
                self.hide_entities()
                self.pause.paused = False  # Hard reset to guarantee pause
                self.pause.set_pause(pause_time=3, func=self.next_level)

    def check_ghost_events(self):
        for ghost in self.ghosts:
            if self.pacman.collide_ghost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.snd_eat_ghost.play()
                    self.pacman.visible = False
                    ghost.visible = False
                    self.update_score(ghost.points)
                    self.text_group.add_text(str(ghost.points), TEAL, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.update_points()
                    self.pause.paused = False  # Hard reset
                    self.pause.set_pause(pause_time=1, func=self.show_entities)
                    ghost.start_spawn()
                    self.nodes.allow_home_access(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        pygame.mixer.stop()  # Silences everything else immediately!
                        self.death_channel.play(self.snd_fail)
                        self.lives -= 1
                        self.life_sprites.remove_image()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.text_group.show_text(GAMEOVERTXT)
                            self.pause.paused = False  # Hard reset
                            if self.game_mode == "ai":
                                self.pause.set_pause(pause_time=3, func=self.restart_ai_game)
                            else:
                                self.pause.set_pause(pause_time=3, func=self.restart_game)
                        else:
                            self.pause.paused = False  # Hard reset
                            self.pause.set_pause(pause_time=3, func=self.reset_level)

    def show_entities(self):
        """Shows the entities on the screen"""
        self.pacman.visible = True
        self.ghosts.show()
        self.text_group.hide_text()

    def hide_entities(self):
        """Hides the entities visible"""
        self.pacman.visible = False
        self.ghosts.hide()

    def next_level(self):
        """Go to the next level"""
        self.show_entities()
        self.level += 1
        self.pause.paused = True
        self.start_game(self.game_mode)
        self.text_group.update_level(self.level)

    def load_title_screen(self):
        self.title_screen = True
        self.screen_state = "title"
        self.ai_countdown_time = 5.0
        self.set_title_screen_background()
        self.title_text = None

    def load_controls_screen(self):
        self.title_screen = True
        self.screen_state = "controls"
        self.set_title_screen_background()

    def load_ai_info_screen(self):
        self.title_screen = True
        self.screen_state = "ai_info"
        self.ai_countdown_time = 5.0
        self.ai_status_message = "Loading saved DQN agent..."
        self.set_title_screen_background()

    def set_title_screen_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def get_state(self):
        """Returns a normalized array representing what the AI 'sees'."""
        if not self.pacman or not self.ghosts:
            return np.zeros(22, dtype=np.float32)

        state = []
        # 1. Pacman's normalized X and Y
        state.extend([self.pacman.position.x / SCREENWIDTH, self.pacman.position.y / SCREENHEIGHT])

        # 2. Ghost Data (4 ghosts * 3 data points = 12 values)
        # We divide by max values to normalize them between 0 and 1 (Neural Networks prefer 0.0 to 1.0)
        for ghost in self.ghosts:
            state.extend([
                ghost.position.x / SCREENWIDTH,
                ghost.position.y / SCREENHEIGHT,
                ghost.mode.current / 3.0  # Mode (0:Scatter, 1:Chase, 2:Freight, 3:Spawn)
            ])

        # 3. Local visibility around Pac-Man.
        # For front, behind, left, and right, the AI sees whether the first and
        # second tiles are open. Each value is 1.0 for open and 0.0 for blocked.
        state.extend(self.get_local_visibility())

        return np.array(state, dtype=np.float32)

    def get_local_visibility(self):
        """Return open/blocked tiles up to two spaces in each relative direction."""
        facing = self.pacman.direction
        if facing == STOP:
            facing = self.pacman.ai_direction if self.pacman.ai_mode else LEFT
        if facing == STOP:
            facing = LEFT

        relative_directions = [
            facing,
            facing * -1,
            self.get_left_turn(facing),
            self.get_right_turn(facing),
        ]
        visibility = []
        for direction in relative_directions:
            visibility.extend(self.get_direction_visibility(direction, distance=2))
        return visibility

    def get_direction_visibility(self, direction, distance):
        """Return open/blocked values from Pac-Man's current node in one direction."""
        visibility = []
        node = self.pacman.node
        for _ in range(distance):
            if (
                direction != STOP
                and node is not None
                and self.pacman.name in node.access[direction]
                and node.neighbors[direction] is not None
            ):
                visibility.append(1.0)
                node = node.neighbors[direction]
            else:
                visibility.append(0.0)
                node = None
        return visibility

    @staticmethod
    def get_left_turn(direction):
        left_turns = {UP: LEFT, LEFT: DOWN, DOWN: RIGHT, RIGHT: UP}
        return left_turns[direction]

    @staticmethod
    def get_right_turn(direction):
        right_turns = {UP: RIGHT, RIGHT: DOWN, DOWN: LEFT, LEFT: UP}
        return right_turns[direction]

    def ai_action_hits_wall(self, direction):
        """Return True when the selected AI direction points into a blocked tile."""
        if not self.pacman or direction == STOP:
            return False
        return not self.pacman.valid_direction(direction)

    def distance_to_nearest_pellet(self):
        """Return Pac-Man's distance to the closest remaining pellet."""
        if not self.pacman or not self.pellets or not self.pellets.pellet_list:
            return None
        return min((self.pacman.position - pellet.position).magnitude() for pellet in self.pellets.pellet_list)

    def distance_to_fruit(self):
        """Return Pac-Man's distance to the active fruit, if one is available."""
        if not self.pacman or self.fruit is None:
            return None
        return (self.pacman.position - self.fruit.position).magnitude()

    def distance_to_nearest_frightened_ghost(self):
        """Return Pac-Man's distance to the nearest edible ghost."""
        if not self.pacman or not self.ghosts:
            return None
        frightened_distances = [
            (self.pacman.position - ghost.position).magnitude()
            for ghost in self.ghosts
            if ghost.mode.current == FREIGHT
        ]
        if not frightened_distances:
            return None
        return min(frightened_distances)

    def distance_to_nearest_dangerous_ghost(self):
        """Return Pac-Man's distance to the nearest active ghost threat."""
        if not self.pacman or not self.ghosts:
            return None
        dangerous_distances = [
            (self.pacman.position - ghost.position).magnitude()
            for ghost in self.ghosts
            if ghost.mode.current not in (FREIGHT, SPAWN)
        ]
        if not dangerous_distances:
            return None
        return min(dangerous_distances)

    @staticmethod
    def reward_for_distance_progress(old_distance, new_distance, weight):
        """Reward moving closer to a target and lightly punish drifting away."""
        if old_distance is None or new_distance is None:
            return 0
        return ((old_distance - new_distance) / TILEWIDTH) * weight

    @staticmethod
    def reward_for_ghost_escape(old_distance, new_distance, danger_radius=TILEWIDTH * 6, weight=0.05):
        """Reward increasing distance from nearby dangerous ghosts."""
        if old_distance is None or new_distance is None or old_distance > danger_radius:
            return 0
        return ((new_distance - old_distance) / TILEWIDTH) * weight

    def step_ai(self, action):
        """Ticks the game forward exactly one frame based on the AI's action."""

        # Map AI Action (0,1,2,3) to pygame Constants
        action_map = {0: UP, 1: DOWN, 2: LEFT, 3: RIGHT}
        selected_direction = action_map[action]
        wall_hit = self.ai_action_hits_wall(selected_direction)
        if self.pacman:
            self.pacman.ai_direction = selected_direction

        old_score = self.score
        old_lives = self.lives
        old_pellet_distance = self.distance_to_nearest_pellet()
        old_fruit_distance = self.distance_to_fruit()
        old_frightened_ghost_distance = self.distance_to_nearest_frightened_ghost()
        old_dangerous_ghost_distance = self.distance_to_nearest_dangerous_ghost()

        # Fast-forward any pauses (like beating a level) so the AI doesn't get stuck waiting
        if self.pause.paused:
            if self.pause.func is not None:
                self.pause.func()  # Execute the pending transition (e.g., next_level) instantly!
            self.pause.paused = False
            self.pause.pause_time = None
            self.show_entities()

        # Tick the game forward
        self.update()
        new_pellet_distance = self.distance_to_nearest_pellet()
        new_fruit_distance = self.distance_to_fruit()
        new_frightened_ghost_distance = self.distance_to_nearest_frightened_ghost()
        new_dangerous_ghost_distance = self.distance_to_nearest_dangerous_ghost()

        # Calculate Reward
        raw_reward = self.score - old_score

        #Scale the game score down so the neural network handles the math better!
        #(e.g., +10 points becomes +0.1 reward)
        divisor = 10.0
        reward = raw_reward / divisor
        # Time Penalty: AI loses 0.1 points every frame to encourage moving fast
        reward -= (0.1 / divisor)
        if wall_hit:
            reward -= (5 / divisor)
        reward += self.reward_for_distance_progress(old_pellet_distance, new_pellet_distance, (2/divisor))
        reward += self.reward_for_distance_progress(old_fruit_distance, new_fruit_distance, (5/divisor))
        reward += self.reward_for_distance_progress(old_frightened_ghost_distance, new_frightened_ghost_distance, (8/divisor))
        reward += self.reward_for_ghost_escape(old_dangerous_ghost_distance, new_dangerous_ghost_distance)

        done = False

        # Massive penalty if AI died this frame.
        # We end the episode on ANY death so the environment perfectly hard-resets.
        if self.lives < old_lives or not self.pacman.alive:
            reward -= 500.0 / divisor
            done = True

            # Level complete bonus
        if self.pellets and self.pellets.is_empty():
            reward += 1000.0 / divisor

        state = self.get_state()
        info = {"score": self.score, "level": self.level}

        return state, reward, done, False, info


if __name__ == "__main__":
    game = GameController()
    game.load_title_screen()
    while True:
        game.update()
