# Tetris AI (Headless + Visual)

This project contains a Tetris environment designed for AI experiments and a visual player built with pygame.

It supports two primary workflows:
- Headless state-based interaction for training and evaluation.
- Visual autoplay for watching a trained model play.

---

## Project Structure

- `tetris.py`
  - Core headless game environment (`TetrisEnv`)
  - Game rules and physics (movement, rotation, locking, line clear, game over)
  - Action API (`step`, `reset`, etc.)
  - Placement API (`get_all_possible_placements`, `execute_placement`)

- `train_with_placements.py`
  - Placement-based model training loop
  - Feature-based linear model (`PlacementLinearModel`)
  - Loss/objective logic (holes, stack height, bumpiness, lines, score)
  - Model save/load
  - Optional visual autoplay after training
  - Play-only mode to load a saved model and watch without training

- `main.py`
  - Lightweight visual renderer and controls for manual/basic environment stepping

- `models/`
  - Saved model files (default: `models/placement_linear_model.npz`)

---

## Requirements

- Python 3.11+
- pygame
- numpy

You already have a virtual environment in `env/` with dependencies installed.

---

## Quick Start

### 1) Activate virtual environment (PowerShell)

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& ".\env\Scripts\Activate.ps1")
```

### 2) Run trained model only (no training)

```powershell
python .\train_with_placements.py --play-only
```

### 3) Train, save, then watch autoplay

```powershell
python .\train_with_placements.py
```

### 4) Train only, no visual window

```powershell
python .\train_with_placements.py --skip-visual
```

---

## Core Concepts

### State Representation

`TetrisEnv.get_state()` returns a tensor of shape `(2, rows, cols)`:
- Channel 0: locked board occupancy (0/1)
- Channel 1: current falling piece occupancy (0/1)

Default size is `(2, 20, 10)`.

### Action Space

`TetrisEnv` supports 6 actions:
- `0` / `noop`
- `1` / `left`
- `2` / `right`
- `3` / `rotate`
- `4` / `soft_drop`
- `5` / `hard_drop`

### Step Return

`step(action)` returns `StepResult`:
- `state`: next state tensor
- `reward`: float reward
- `done`: whether game is over
- `info`: score/lines/steps/piece metadata

---

## Placement-Based Decision API

These two methods are the key to your placement-evaluation strategy.

### `get_all_possible_placements()`

Computes all valid landing configurations for the current falling piece.

Returns a list of dicts. Each item includes:
- `board_after`: board if this placement is chosen
- `board_before`: board right before locking (for debugging/analysis)
- `final_rotation`: target rotation index
- `final_x`: target x column position
- `lines_cleared`: lines cleared by this placement
- `resulting_score`: score after applying this placement

This is used to evaluate candidate final configurations directly.

### `execute_placement(final_rotation, final_x)`

Moves the active piece to a selected `(rotation, x)` and performs a hard drop.

This is used after your model chooses the best candidate from `get_all_possible_placements()`.

---

## Training Script Documentation (`train_with_placements.py`)

### Model

`PlacementLinearModel` scores each candidate placement using features:
- `bias`
- `lines`
- `holes`
- `aggregate_height`
- `bumpiness`

Score calculation:
- For all placements, compute feature vector.
- Compute `features @ weights`.
- Choose placement with maximum predicted score.

### Training Objective

The script optimizes a loss that explicitly encourages healthy board structure:
- Penalize holes
- Penalize aggregate stack height
- Penalize bumpiness
- Reward cleared lines
- Reward score

Loss (lower is better):

```text
loss = 4.0*holes + 0.45*height + 0.25*bumpiness - 10.0*lines - 0.008*score
```

Optimization objective is `-loss` (higher is better) for easier candidate search.

### Training Loop

- Start from initial heuristic weights.
- For each generation:
  - Sample random weight perturbations (candidates).
  - Evaluate each candidate on one or more episodes.
  - Keep best candidate if objective improves.
  - Adapt mutation scale (`sigma`) over time.

### Debug and Heartbeats

With `--debug`, script prints:
- Per-candidate metrics (objective/loss/score/lines/holes/height)
- Per-generation summaries

With `--progress-every N`, script prints periodic heartbeat lines during long episodes:
- placements count
- score
- lines
- holes
- height

---

## CLI Reference (`train_with_placements.py`)

### Main Arguments

- `--generations` (default: `5`)
  - Number of optimization generations.

- `--candidates` (default: `8`)
  - Number of mutated candidates per generation.

- `--eval-episodes` (default: `2`)
  - Episodes per candidate evaluation.

- `--max-steps` (default: `1200`)
  - Placement decisions per episode cap.

- `--model-path` (default: `models/placement_linear_model.npz`)
  - Save/load path for model weights.

- `--debug`
  - Enables detailed training output.

- `--progress-every` (default: `100`)
  - Heartbeat interval in placements.

- `--skip-visual`
  - Disable visual autoplay after training.

- `--play-only`
  - Skip training entirely.
  - Load model from `--model-path` and open visual autoplay.

---

## Common Commands

### Watch saved model play (no training)

```powershell
python .\train_with_placements.py --play-only
```

### Watch a specific saved model

```powershell
python .\train_with_placements.py --play-only --model-path .\models\placement_linear_model.npz
```

### Fast debug run

```powershell
python .\train_with_placements.py --generations 1 --candidates 2 --eval-episodes 1 --max-steps 300 --skip-visual --debug --progress-every 50
```

### Full training with debug, then autoplay

```powershell
python .\train_with_placements.py --debug
```

### Training only (no pygame window)

```powershell
python .\train_with_placements.py --skip-visual
```

---

## Visual Renderer (`main.py`)

`main.py` includes a renderer class over `TetrisEnv` and supports keyboard control.

Basic run:

```powershell
python .\main.py
```

Headless demo run:

```powershell
python .\main.py headless
```

---

## File-Level API Notes

### `tetris.py` -> `TetrisEnv`

Primary methods:
- `reset() -> np.ndarray`
- `step(action) -> StepResult`
- `get_state() -> np.ndarray`
- `get_state_dict() -> dict`
- `sample_action() -> int`
- `get_all_possible_placements() -> list[dict]`
- `execute_placement(final_rotation, final_x) -> StepResult`

### `train_with_placements.py` -> `PlacementLinearModel`

Primary methods:
- `extract_features(board_after, lines_cleared) -> np.ndarray`
- `score_placements(placements) -> np.ndarray`
- `choose_best(placements) -> dict`
- `save(file_path)`
- `load(file_path)`

---

## Troubleshooting

### Script seems stuck at startup or after pygame banner

- Enable debug output:

```powershell
python .\train_with_placements.py --debug
```

- Add frequent heartbeat logs:

```powershell
python .\train_with_placements.py --debug --progress-every 25
```

This confirms training is running and shows intermediate metrics.

### `--play-only` does not start game

Possible causes:
- Model file missing at `--model-path`
- You passed both `--play-only` and `--skip-visual`

Fix by ensuring a valid model file exists and run only:

```powershell
python .\train_with_placements.py --play-only
```

### No saved model yet

Train once quickly:

```powershell
python .\train_with_placements.py --generations 1 --candidates 2 --eval-episodes 1 --max-steps 300 --skip-visual
```

---

## Suggested Next Improvements

- Replace linear scoring model with a neural network (PyTorch).
- Add replay buffer and TD-learning / policy gradient.
- Persist run metrics to CSV for plotting.
- Add unit tests for placement enumeration correctness.
- Add deterministic evaluation benchmark with fixed seeds.
