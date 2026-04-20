"""
Train a placement-based Tetris agent, save it, then run visual autoplay.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pygame

from tetris import TetrisEnv


PIECE_COLORS = {
    "I": (69, 123, 157),
    "J": (29, 53, 87),
    "L": (230, 111, 81),
    "O": (233, 196, 106),
    "S": (42, 157, 143),
    "Z": (214, 40, 40),
    "T": (106, 76, 147),
}


@dataclass
class EpisodeStats:
    score: int
    lines: int
    placements: int
    holes: float
    aggregate_height: float
    bumpiness: float


class PlacementLinearModel:
    """
    Lightweight linear model over board features for placement scoring.
    """

    FEATURE_NAMES = ["bias", "lines", "holes", "aggregate_height", "bumpiness"]

    def __init__(self, weights: np.ndarray | None = None) -> None:
        if weights is None:
            # Start with a sane heuristic prior.
            self.weights = np.array([0.0, 3.0, -1.0, -0.2, -0.4], dtype=np.float32)
        else:
            self.weights = np.asarray(weights, dtype=np.float32)

    def extract_features(self, board_after: np.ndarray, lines_cleared: int) -> np.ndarray:
        heights = self._column_heights(board_after)
        holes = self._count_holes(board_after)
        aggregate_height = float(np.sum(heights))
        bumpiness = float(np.sum(np.abs(np.diff(heights))))
        return np.array([1.0, float(lines_cleared), holes, aggregate_height, bumpiness], dtype=np.float32)

    def score_placements(self, placements: List[Dict]) -> np.ndarray:
        features = np.stack(
            [self.extract_features(p["board_after"], p["lines_cleared"]) for p in placements],
            axis=0,
        )
        return features @ self.weights

    def choose_best(self, placements: List[Dict]) -> Dict:
        scores = self.score_placements(placements)
        return placements[int(np.argmax(scores))]

    @staticmethod
    def _column_heights(board: np.ndarray) -> np.ndarray:
        rows, cols = board.shape
        heights = np.zeros(cols, dtype=np.float32)
        for c in range(cols):
            filled_rows = np.where(board[:, c] == 1)[0]
            heights[c] = 0.0 if filled_rows.size == 0 else float(rows - filled_rows[0])
        return heights

    @staticmethod
    def _count_holes(board: np.ndarray) -> float:
        holes = 0
        for col in range(board.shape[1]):
            filled = False
            for row in range(board.shape[0]):
                if board[row, col] == 1:
                    filled = True
                elif filled and board[row, col] == 0:
                    holes += 1
        return float(holes)

    def save(self, file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        np.savez(file_path, weights=self.weights, feature_names=np.array(self.FEATURE_NAMES, dtype="U32"))

    @classmethod
    def load(cls, file_path: str) -> "PlacementLinearModel":
        data = np.load(file_path)
        return cls(weights=data["weights"])


def run_episode(
    env: TetrisEnv,
    model: PlacementLinearModel,
    max_steps: int,
    debug: bool = False,
    progress_every: int = 100,
) -> EpisodeStats:
    env.reset()
    placements_used = 0

    for _ in range(max_steps):
        if env.done:
            break

        placements = env.get_all_possible_placements()
        if not placements:
            break

        best = model.choose_best(placements)
        env.execute_placement(best["final_rotation"], best["final_x"])
        placements_used += 1

        if debug and progress_every > 0 and placements_used % progress_every == 0:
            heights = model._column_heights(env.board)
            holes = model._count_holes(env.board)
            aggregate_height = float(np.sum(heights))
            print(
                f"    Heartbeat placements={placements_used}, score={env.score}, "
                f"lines={env.lines_cleared}, holes={holes:.1f}, height={aggregate_height:.1f}"
            )

    heights = model._column_heights(env.board)
    holes = model._count_holes(env.board)
    aggregate_height = float(np.sum(heights))
    bumpiness = float(np.sum(np.abs(np.diff(heights))))

    return EpisodeStats(
        score=env.score,
        lines=env.lines_cleared,
        placements=placements_used,
        holes=holes,
        aggregate_height=aggregate_height,
        bumpiness=bumpiness,
    )


def evaluate_weights(
    weights: np.ndarray,
    episodes: int,
    max_steps: int,
    seed: int = 42,
    debug: bool = False,
    progress_every: int = 100,
) -> Tuple[float, Dict[str, float]]:
    model = PlacementLinearModel(weights)
    env = TetrisEnv(seed=seed)
    scores: List[int] = []
    lines: List[int] = []
    holes: List[float] = []
    heights: List[float] = []
    bumpiness_values: List[float] = []

    for episode in range(episodes):
        env.random.seed(seed + episode)
        stats = run_episode(
            env,
            model,
            max_steps=max_steps,
            debug=debug,
            progress_every=progress_every,
        )
        scores.append(stats.score)
        lines.append(stats.lines)
        holes.append(stats.holes)
        heights.append(stats.aggregate_height)
        bumpiness_values.append(stats.bumpiness)

        if debug:
            print(
                f"  Eval Ep {episode + 1}/{episodes}: score={stats.score}, lines={stats.lines}, "
                f"holes={stats.holes:.1f}, height={stats.aggregate_height:.1f}, bumpiness={stats.bumpiness:.1f}"
            )

    mean_score = float(np.mean(scores))
    mean_lines = float(np.mean(lines))
    mean_holes = float(np.mean(holes))
    mean_height = float(np.mean(heights))
    mean_bumpiness = float(np.mean(bumpiness_values))

    # Explicit loss: lower is better.
    # Penalize structural instability (holes/height/bumpiness), reward cleared lines and score.
    loss = (
        (4.0 * mean_holes)
        + (0.45 * mean_height)
        + (0.25 * mean_bumpiness)
        - (10.0 * mean_lines)
        - (0.008 * mean_score)
    )

    # Keep objective for optimizer in "higher is better" form.
    objective = -loss
    return objective, {
        "mean_score": mean_score,
        "mean_lines": mean_lines,
        "mean_holes": mean_holes,
        "mean_height": mean_height,
        "mean_bumpiness": mean_bumpiness,
        "loss": loss,
    }


def train_model(
    generations: int = 8,
    candidates_per_generation: int = 12,
    eval_episodes: int = 2,
    max_steps: int = 2000,
    debug: bool = False,
    progress_every: int = 100,
) -> PlacementLinearModel:
    rng = np.random.default_rng(42)
    best_weights = np.array([0.0, 3.0, -1.0, -0.2, -0.4], dtype=np.float32)
    best_objective, best_metrics = evaluate_weights(
        best_weights,
        eval_episodes,
        max_steps,
        debug=debug,
        progress_every=progress_every,
    )

    print("Starting training")
    print(
        f"Initial objective={best_objective:.2f}, loss={best_metrics['loss']:.2f}, "
        f"mean_score={best_metrics['mean_score']:.1f}, "
        f"mean_lines={best_metrics['mean_lines']:.2f}, "
        f"mean_holes={best_metrics['mean_holes']:.2f}, "
        f"mean_height={best_metrics['mean_height']:.2f}"
    )

    sigma = 0.35
    for generation in range(1, generations + 1):
        generation_best_obj = best_objective
        generation_best_weights = best_weights.copy()

        for candidate_index in range(1, candidates_per_generation + 1):
            candidate = best_weights + rng.normal(0.0, sigma, size=best_weights.shape).astype(np.float32)
            objective, metrics = evaluate_weights(
                candidate,
                eval_episodes,
                max_steps,
                debug=debug,
                progress_every=progress_every,
            )

            if debug:
                print(
                    f"  Gen {generation} Candidate {candidate_index}/{candidates_per_generation}: "
                    f"objective={objective:.2f}, loss={metrics['loss']:.2f}, "
                    f"score={metrics['mean_score']:.1f}, lines={metrics['mean_lines']:.2f}, "
                    f"holes={metrics['mean_holes']:.2f}, height={metrics['mean_height']:.2f}"
                )

            if objective > generation_best_obj:
                generation_best_obj = objective
                generation_best_weights = candidate
                if debug:
                    print("    -> New generation best")

        improved = generation_best_obj > best_objective
        if improved:
            best_weights = generation_best_weights
            best_objective, best_metrics = evaluate_weights(
                best_weights,
                eval_episodes,
                max_steps,
                debug=False,
                progress_every=progress_every,
            )
            sigma = max(0.12, sigma * 0.95)
        else:
            sigma = min(0.60, sigma * 1.10)

        print(
            f"Gen {generation}: objective={best_objective:.2f}, loss={best_metrics['loss']:.2f}, "
            f"mean_score={best_metrics['mean_score']:.1f}, "
            f"mean_lines={best_metrics['mean_lines']:.2f}, sigma={sigma:.3f}"
        )
        if debug:
            print(
                f"  Debug Gen {generation}: holes={best_metrics['mean_holes']:.2f}, "
                f"height={best_metrics['mean_height']:.2f}, bumpiness={best_metrics['mean_bumpiness']:.2f}"
            )

    print(f"Final learned weights: {best_weights.tolist()}")

    return PlacementLinearModel(best_weights)


def render_board(screen: pygame.Surface, env: TetrisEnv, cell_size: int, margin: int, font: pygame.font.Font) -> None:
    screen.fill((15, 18, 22))

    def to_rect(x: int, y: int) -> pygame.Rect:
        return pygame.Rect(
            margin + x * cell_size,
            margin + y * cell_size,
            cell_size,
            cell_size,
        )

    for y in range(env.rows):
        for x in range(env.cols):
            rect = to_rect(x, y)
            pygame.draw.rect(screen, (35, 40, 48), rect, width=1)
            if env.board[y, x] == 1:
                pygame.draw.rect(screen, (100, 175, 255), rect.inflate(-2, -2))

    color = PIECE_COLORS.get(env.current_kind, (240, 240, 240))
    for x, y in env.active_cells:
        if y >= 0:
            pygame.draw.rect(screen, color, to_rect(x, y).inflate(-2, -2))

    hud_x = margin * 2 + env.cols * cell_size
    lines = [
        "TRAINED AGENT",
        f"Score: {env.score}",
        f"Lines: {env.lines_cleared}",
        f"Piece: {env.current_kind}",
        "",
        "Esc = Quit",
    ]
    for idx, text in enumerate(lines):
        if text:
            surf = font.render(text, True, (225, 230, 240))
            screen.blit(surf, (hud_x, margin + idx * 28))

    if env.done:
        over = font.render("GAME OVER", True, (255, 120, 120))
        screen.blit(over, (margin + 2 * cell_size, margin + env.rows * cell_size // 2))


def play_visual_with_model(model: PlacementLinearModel, tick_ms: int = 120, max_steps: int = 3000) -> None:
    pygame.init()
    env = TetrisEnv(seed=123)
    env.reset()

    cell_size = 32
    margin = 20
    width = margin * 2 + env.cols * cell_size + 220
    height = margin * 2 + env.rows * cell_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Tetris AI - Trained Model")
    font = pygame.font.SysFont("consolas", 22)
    clock = pygame.time.Clock()

    running = True
    steps = 0
    last_tick = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        now = pygame.time.get_ticks()
        if not env.done and now - last_tick >= tick_ms and steps < max_steps:
            placements = env.get_all_possible_placements()
            if placements:
                best = model.choose_best(placements)
                env.execute_placement(best["final_rotation"], best["final_x"])
            else:
                env.done = True
            steps += 1
            last_tick = now

        render_board(screen, env, cell_size, margin, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=5)
    parser.add_argument("--candidates", type=int, default=8)
    parser.add_argument("--eval-episodes", type=int, default=2)
    parser.add_argument("--max-steps", type=int, default=1200)
    parser.add_argument("--model-path", type=str, default="models/placement_linear_model.npz")
    parser.add_argument("--play-only", action="store_true")
    parser.add_argument("--skip-visual", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--progress-every", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.play_only:
        if not os.path.exists(args.model_path):
            print(
                f"Model file not found at {args.model_path}. "
                "Train once first, or pass --model-path to an existing model."
            )
            return
        if args.skip_visual:
            print("--play-only used with --skip-visual; nothing to run.")
            return

        loaded_model = PlacementLinearModel.load(args.model_path)
        print(f"Loaded model from {args.model_path}")
        print("Opening visual autoplay without training")
        play_visual_with_model(loaded_model)
        return

    trained_model = train_model(
        generations=args.generations,
        candidates_per_generation=args.candidates,
        eval_episodes=args.eval_episodes,
        max_steps=args.max_steps,
        debug=args.debug,
        progress_every=args.progress_every,
    )

    trained_model.save(args.model_path)
    print(f"Saved trained model to {args.model_path}")

    if not args.skip_visual:
        loaded_model = PlacementLinearModel.load(args.model_path)
        print("Opening visual autoplay with saved model")
        play_visual_with_model(loaded_model)


if __name__ == "__main__":
    main()
