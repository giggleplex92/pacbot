# PacmanAI

PacmanAI is a Python/Pygame Pac-Man project with a reinforcement learning wrapper for training a Deep Q-Network agent. The core game can be played directly, and `AI_Player.py` exposes the game as a Gymnasium environment for Stable-Baselines3.

## Features

- Playable Pac-Man-style game built with Pygame
- Classic ghost modes: scatter, chase, frightened, and spawn/return-home behavior
- Character-specific ghost targeting for Blinky, Pinky, Inky, and Clyde
- Pellet, power pellet, fruit, score, lives, high-score, and level systems
- Sprite, font, maze, and sound assets included in the repository
- Gymnasium-compatible `PacmanEnv` for DQN training
- Saved DQN model artifact: `pacman_dqn_agent.zip`
- TensorBoard training logs under `pacman_tensorboard/`

## Project Structure

```text
.
├── AI_Player.py                  # Gymnasium environment and DQN training entry point
├── run.py                   # Main Pygame game controller and playable entry point
├── pacman.py                # Pac-Man entity and keyboard/AI movement handling
├── ghosts.py                # Ghost classes and ghost group behavior
├── modes.py                 # Ghost mode state machine
├── nodes.py                 # Maze graph and movement node system
├── pellets.py               # Pellet and power pellet logic
├── fruit.py                 # Fruit spawning and scoring
├── sprites.py               # Sprite loading and animation support
├── constants.py             # Game constants, colors, speeds, and scoring values
├── maze_data.py             # Maze metadata and portal/home-node setup
├── Mazes/                   # Maze layout text files
├── Sounds/                  # Game sound effects
├── pacman_dqn_agent.zip     # Saved Stable-Baselines3 DQN model
└── pacman_tensorboard/      # TensorBoard logs from training
```

## Requirements

This project was developed with Python 3.14 in the included local virtual environment. It should also work on a modern Python 3 release supported by the dependencies.

For playing the game:

```bash
python -m pip install pygame-ce numpy
```

For training the AI:

```bash
python -m pip install pygame-ce numpy gymnasium stable-baselines3 tensorboard
```

`stable-baselines3` will install PyTorch and other machine learning dependencies.

## Running the Game

From the project root:

```bash
python run.py
```

Controls:

- `1` or `P`: choose player mode from the title screen
- `2` or `A`: choose AI mode from the title screen
- `Space`: start from the player controls screen, or pause/resume during play
- Arrow keys: move Pac-Man
- `Esc` or `Backspace`: return to the main title screen from an instruction screen

Player mode disables Pac-Man's AI input so the arrow keys control movement and the lives system works normally. AI mode loads the saved `pacman_dqn_agent.zip` model, shows a short countdown, and lets the trained DQN agent play.

The game stores the current high score in `highscore.txt`.

## Training the DQN Agent

Run:

```bash
python AI_Player.py
```

This creates a headless, muted `PacmanEnv`, trains a Stable-Baselines3 DQN model for 50,000 timesteps, writes TensorBoard logs to `pacman_tensorboard/`, and saves the model as `pacman_dqn_agent.zip`. To watch the trained model play with the normal window and sounds, run `python run.py` and choose AI mode.

To monitor training:

```bash
tensorboard --logdir pacman_tensorboard
```

Then open the TensorBoard URL shown in the terminal.

## Environment Details

`AI_Player.py` defines `PacmanEnv`, a Gymnasium environment backed by the Pygame game controller.

- Action space: `Discrete(4)`
- Actions: `0 = up`, `1 = down`, `2 = left`, `3 = right`
- Observation shape: `(22,)`
- Observation data:
  - Pac-Man normalized `x, y`
  - Four ghosts, each represented by normalized `x, y` and current mode
  - One- and two-tile visibility in front, behind, left, and right
- Reward:
  - Scaled score delta from the game
  - Small time penalty each frame
  - Small penalty for trying to move into a wall
  - Small reward for moving toward pellets, fruit, and frightened ghosts
  - Small reward for moving away from nearby dangerous ghosts
  - Large penalty on death
  - Bonus when all pellets are cleared

The training environment runs headless and muted. `run.py` still renders the visible game and plays sound when you choose AI mode.

## Notes

- Asset paths are relative, so run commands from the project root.
- `MazeData` currently rotates through the configured maze dictionary; only `Maze1` is active in the current code.
- `pacman_dqn_agent.zip`, `pacman_tensorboard/`, and `highscore.txt` are runtime/training artifacts. Keep them if you want to preserve the trained model, logs, or high score.
