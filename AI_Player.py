"""
Run this file to train a new AI agent to play pacman.
do this BEFORE trying it out in "run.py"
"""

import os

# Training should run in the background. These must be set before importing
# pygame through run.py so SDL does not open a window or use real audio output.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from stable_baselines3 import DQN
from run import GameController


class PacmanEnv(gym.Env):
    """Custom Environment that follows gym interface for Pac-Man"""
    metadata = {"render_modes": ["human"]}

    def __init__(self, render_mode=None):
        super(PacmanEnv, self).__init__()

        # Create the game instance
        show_game = render_mode == "human"
        self.game = GameController(render_enabled=show_game, sound_enabled=show_game)
        self.render_mode = render_mode

        # ACTION SPACE: 4 possible moves (0: UP, 1: DOWN, 2: LEFT, 3: RIGHT)
        self.action_space = spaces.Discrete(4)

        # OBSERVATION SPACE: A 1D array of 22 floats:
        # - Pac-Man X/Y
        # - 4 ghosts with X/Y/mode
        # - 8 local visibility values for one and two tiles in each direction:
        #   front, behind, left, and right
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(22,), dtype=np.float32)

    def step(self, action):
        # Pass the action to the game and get the results
        obs, reward, done, truncated, info = self.game.step_ai(action)
        return obs, reward, done, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Hard reset the game
        self.game.restart_game()

        # Force start sequence bypass
        self.game.title_screen = False
        self.game.start_game()
        self.game.pause.paused = False
        self.game.pause.pause_time = None
        self.game.show_entities()

        obs = self.game.get_state()
        info = {}
        return obs, info

    def render(self):
        # We rely on run.py's internal render inside step_ai, but Gym requires this method
        pass

    def close(self):
        import pygame
        pygame.quit()


if __name__ == "__main__":
    print("Initializing Pac-Man Environment...")
    env = PacmanEnv()

    # Optional: Verifies the environment matches Gymnasium standards
    # check_env(env) 

    # Initialize the Deep Q-Network AI
    # MlpPolicy means it uses a standard Neural Network (Multilayer Perceptron)
    print("Building DQN Agent...")
    model = DQN(
        "MlpPolicy",
        env,

        # verbose controls how much training information prints in the terminal.
        # 0 is silent, 1 prints useful progress, and 2 prints extra debugging detail.
        verbose=1,

        # learning_rate controls how aggressively the neural network updates.
        # Higher values can learn faster but may become unstable; lower values are
        # steadier but usually need more training time.
        learning_rate=0.0001,

        # buffer_size is the number of past experiences the agent remembers.
        # A larger buffer gives more varied training examples but uses more memory
        # and can make the agent learn from older behavior for longer.
        buffer_size=100000,

        # exploration_fraction is the portion of training spent gradually reducing
        # random actions. Higher values make the agent explore for longer; lower
        # values make it commit to learned behavior sooner.
        exploration_fraction=0.3,

        # batch_size is how many remembered experiences are sampled per update.
        # Larger batches can make updates smoother but require more memory; smaller
        # batches are lighter but can make learning noisier.
        batch_size=128,

        # max_grad_norm clips very large neural-network updates.
        # Raising it allows bigger jumps; lowering it makes training more cautious.
        max_grad_norm=10,

        # target_update_interval controls how often DQN refreshes its target network.
        # Smaller values react faster to new learning; larger values can make training
        # more stable but slower to adapt.
        target_update_interval=1000,

        #Final value of random action probability
        exploration_final_eps=0.05,

        # tensorboard_log is where training metrics are written. Run
        # `tensorboard --logdir pacman_tensorboard` to view rewards, losses, and
        # other learning curves in your browser.
        tensorboard_log="./pacman_tensorboard/"
    )

    print("Starting background training...")
    # Train for 1,000,000 frames.
    model.learn(total_timesteps=5000000, log_interval=4)

    # Save the brain so you don't have to retrain from scratch next time
    model.save("pacman_dqn_agent")

    print("Training Complete!")
