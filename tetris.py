from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import numpy as np

Action = Union[int, str]

# Each tuple in a rotation is (dx, dy) from the piece origin.
PIECES: Dict[str, List[List[Tuple[int, int]]]] = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
}

ACTIONS: Dict[Union[int, str], int] = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    "noop": 0,
    "left": 1,
    "right": 2,
    "rotate": 3,
    "soft_drop": 4,
    "hard_drop": 5,
}

LINE_CLEAR_REWARD = {0: 0.0, 1: 1.0, 2: 3.0, 3: 5.0, 4: 8.0}


@dataclass
class StepResult:
    state: np.ndarray
    reward: float
    done: bool
    info: Dict[str, Union[int, str, float]]


class TetrisEnv:
    """
    Headless Tetris environment for AI training.

    State format:
    - state[0]: locked blocks on the board (0/1)
    - state[1]: current falling piece occupancy (0/1)
    shape: (2, rows, cols)
    """

    def __init__(self, rows: int = 20, cols: int = 10, seed: int | None = None) -> None:
        self.rows = rows
        self.cols = cols
        self.random = random.Random(seed)
        self.board = np.zeros((rows, cols), dtype=np.int8)
        self.action_space_n = 6
        self._bag: List[str] = []

        self.score = 0
        self.lines_cleared = 0
        self.steps = 0
        self.done = False

        self.current_kind = ""
        self.current_rotation = 0
        self.current_x = 0
        self.current_y = 0

        self.reset()

    def reset(self) -> np.ndarray:
        self.board.fill(0)
        self.score = 0
        self.lines_cleared = 0
        self.steps = 0
        self.done = False
        self._bag = []
        self._spawn_piece()
        return self.get_state()

    def _refill_bag(self) -> None:
        self._bag = list(PIECES.keys())
        self.random.shuffle(self._bag)

    def _piece_cells(
        self, kind: str, rotation: int, x: int, y: int
    ) -> List[Tuple[int, int]]:
        return [(x + dx, y + dy) for dx, dy in PIECES[kind][rotation]]

    def _is_valid(self, cells: List[Tuple[int, int]]) -> bool:
        for x, y in cells:
            if x < 0 or x >= self.cols or y >= self.rows:
                return False
            if y >= 0 and self.board[y, x] == 1:
                return False
        return True

    def _spawn_piece(self) -> bool:
        if not self._bag:
            self._refill_bag()

        self.current_kind = self._bag.pop()
        self.current_rotation = 0
        self.current_x = (self.cols // 2) - 2
        self.current_y = -1

        if not self._is_valid(self.active_cells):
            self.done = True
            return False
        return True

    @property
    def active_cells(self) -> List[Tuple[int, int]]:
        return self._piece_cells(
            self.current_kind,
            self.current_rotation,
            self.current_x,
            self.current_y,
        )

    def _try_move(self, dx: int, dy: int, rotation_delta: int = 0) -> bool:
        new_rotation = (self.current_rotation + rotation_delta) % len(PIECES[self.current_kind])
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        cells = self._piece_cells(self.current_kind, new_rotation, new_x, new_y)

        if not self._is_valid(cells):
            return False

        self.current_rotation = new_rotation
        self.current_x = new_x
        self.current_y = new_y
        return True

    def _clear_lines(self) -> int:
        full_mask = np.all(self.board == 1, axis=1)
        cleared = int(np.sum(full_mask))
        if cleared == 0:
            return 0

        remaining = self.board[~full_mask]
        new_rows = np.zeros((cleared, self.cols), dtype=np.int8)
        self.board = np.vstack((new_rows, remaining))
        return cleared

    def _lock_piece(self) -> int:
        for x, y in self.active_cells:
            if y < 0:
                self.done = True
                return 0
            self.board[y, x] = 1

        cleared = self._clear_lines()
        self.lines_cleared += cleared
        self.score += [0, 100, 300, 500, 800][cleared]
        self._spawn_piece()
        return cleared

    def get_state(self) -> np.ndarray:
        state = np.zeros((2, self.rows, self.cols), dtype=np.float32)
        state[0] = self.board
        for x, y in self.active_cells:
            if 0 <= y < self.rows:
                state[1, y, x] = 1.0
        return state

    def get_state_dict(self) -> Dict[str, Union[np.ndarray, str, int, bool]]:
        return {
            "board": self.board.copy(),
            "active_cells": np.array(self.active_cells, dtype=np.int16),
            "piece": self.current_kind,
            "rotation": self.current_rotation,
            "score": self.score,
            "lines_cleared": self.lines_cleared,
            "done": self.done,
        }

    def sample_action(self) -> int:
        return self.random.randint(0, self.action_space_n - 1)

    def step(self, action: Action = 0) -> StepResult:
        if self.done:
            return StepResult(self.get_state(), 0.0, True, self._build_info())

        self.steps += 1
        action_id = ACTIONS.get(action, 0)
        reward = 0.0
        locked_this_step = False

        if action_id == 1:
            self._try_move(-1, 0)
        elif action_id == 2:
            self._try_move(1, 0)
        elif action_id == 3:
            self._try_move(0, 0, rotation_delta=1)
        elif action_id == 4:
            moved = self._try_move(0, 1)
            if moved:
                reward += 0.02
            else:
                cleared = self._lock_piece()
                reward += LINE_CLEAR_REWARD[cleared]
                locked_this_step = True
        elif action_id == 5:
            drop_distance = 0
            while self._try_move(0, 1):
                drop_distance += 1
            cleared = self._lock_piece()
            reward += 0.02 * drop_distance + LINE_CLEAR_REWARD[cleared]
            locked_this_step = True

        # Gravity tick: one downward move per environment step.
        if not self.done and not locked_this_step:
            if not self._try_move(0, 1):
                cleared = self._lock_piece()
                reward += LINE_CLEAR_REWARD[cleared]

        if self.done:
            reward -= 2.0

        return StepResult(
            state=self.get_state(),
            reward=reward,
            done=self.done,
            info=self._build_info(),
        )

    def get_all_possible_placements(self) -> List[Dict]:
        """
        Compute all possible landing configurations for the current falling piece.
        
        Returns a list of placement dicts, each containing:
        - board_after: np.ndarray – the board state after piece lands
        - final_rotation: int – rotation index of piece at landing
        - final_x: int – x position of piece at landing
        - moves: List[int] – sequence of action IDs to reach this placement
        - lines_cleared: int – number of lines that would clear
        - resulting_score: int – score if this placement is taken
        
        Sorted by x position and rotation for consistency.
        Model can then score each and pick the best one.
        """
        placements = []
        
        # Save current state to restore later
        saved_rotation = self.current_rotation
        saved_x = self.current_x
        saved_y = self.current_y
        saved_board = self.board.copy()
        
        piece = self.current_kind
        max_rotations = len(PIECES[piece])
        
        # Try all rotations
        for rotation in range(max_rotations):
            # Try all x positions
            for x in range(-2, self.cols + 2):
                # Simulate placing this piece at (x, rotation)
                self.current_rotation = rotation
                self.current_x = x
                self.current_y = -1
                
                # Check if starting position is valid
                if not self._is_valid(self.active_cells):
                    continue
                
                # Drop piece to bottom (simulate hard drop)
                drop_distance = 0
                while self._try_move(0, 1):
                    drop_distance += 1
                
                # Check if piece is still valid after drop (shouldn't fail, but safety check)
                if not self._is_valid(self.active_cells):
                    self.current_rotation = saved_rotation
                    self.current_x = saved_x
                    self.current_y = saved_y
                    self.board = saved_board.copy()
                    continue
                
                # Lock the piece and compute resulting board state
                board_before_lock = self.board.copy()
                for px, py in self.active_cells:
                    if py >= 0:
                        self.board[py, px] = 1
                
                lines_cleared = self._clear_lines()
                resulting_score = self.score + [0, 100, 300, 500, 800][lines_cleared]
                
                # Record this placement
                placements.append({
                    "board_after": self.board.copy(),
                    "board_before": board_before_lock.copy(),
                    "final_rotation": rotation,
                    "final_x": x,
                    "lines_cleared": lines_cleared,
                    "resulting_score": resulting_score,
                })
                
                # Restore board for next iteration
                self.board = saved_board.copy()
        
        # Restore original state
        self.current_rotation = saved_rotation
        self.current_x = saved_x
        self.current_y = saved_y
        self.board = saved_board
        
        return placements
    
    def execute_placement(self, final_rotation: int, final_x: int) -> StepResult:
        """
        Execute moves to reach a specific placement (rotation, x) and hard-drop.
        Returns the step result after landing.
        
        This is useful after the model picks the best placement from
        get_all_possible_placements().
        """
        # Rotate to target rotation
        while self.current_rotation != final_rotation:
            self._try_move(0, 0, rotation_delta=1)
        
        # Move to target x position
        if self.current_x < final_x:
            while self.current_x < final_x:
                if not self._try_move(1, 0):
                    break
        elif self.current_x > final_x:
            while self.current_x > final_x:
                if not self._try_move(-1, 0):
                    break
        
        # Hard drop
        return self.step(5)

    def _build_info(self) -> Dict[str, Union[int, str, float]]:
        return {
            "score": self.score,
            "lines_cleared": self.lines_cleared,
            "steps": self.steps,
            "piece": self.current_kind,
        }