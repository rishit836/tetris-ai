import sys
from typing import List, Tuple

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


class TetrisRenderer:
    def __init__(
        self,
        env: TetrisEnv,
        cell_size: int = 32,
        margin: int = 20,
        fps: int = 60,
        tick_ms: int = 120,
    ) -> None:
        pygame.init()
        self.env = env
        self.cell_size = cell_size
        self.margin = margin
        self.fps = fps
        self.tick_ms = tick_ms

        width = self.margin * 2 + env.cols * self.cell_size + 180
        height = self.margin * 2 + env.rows * self.cell_size
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22)
        self.running = True

    def _to_rect(self, x: int, y: int) -> pygame.Rect:
        return pygame.Rect(
            self.margin + x * self.cell_size,
            self.margin + y * self.cell_size,
            self.cell_size,
            self.cell_size,
        )

    def _draw_board(self) -> None:
        self.screen.fill((15, 18, 22))

        # Locked board cells.
        for y in range(self.env.rows):
            for x in range(self.env.cols):
                rect = self._to_rect(x, y)
                pygame.draw.rect(self.screen, (35, 40, 48), rect, width=1)
                if self.env.board[y, x] == 1:
                    pygame.draw.rect(self.screen, (100, 175, 255), rect.inflate(-2, -2))

        # Active falling piece cells.
        piece_color = PIECE_COLORS.get(self.env.current_kind, (240, 240, 240))
        for x, y in self.env.active_cells:
            if y < 0:
                continue
            pygame.draw.rect(self.screen, piece_color, self._to_rect(x, y).inflate(-2, -2))

        hud_x = self.margin * 2 + self.env.cols * self.cell_size
        hud_lines: List[Tuple[str, int]] = [
            ("TETRIS", 0),
            (f"Score: {self.env.score}", 2),
            (f"Lines: {self.env.lines_cleared}", 3),
            (f"Piece: {self.env.current_kind}", 4),
            ("", 5),
            ("Controls", 6),
            ("Left/Right", 7),
            ("Up = Rotate", 8),
            ("Down = Soft", 9),
            ("Space = Hard", 10),
            ("R = Reset", 11),
            ("Esc = Quit", 12),
        ]
        for text, row in hud_lines:
            if text:
                surface = self.font.render(text, True, (225, 230, 240))
                self.screen.blit(surface, (hud_x, self.margin + row * 28))

        if self.env.done:
            overlay = self.font.render("GAME OVER", True, (255, 120, 120))
            self.screen.blit(
                overlay,
                (self.margin + 2 * self.cell_size, self.margin + self.env.rows * self.cell_size // 2),
            )

    def run(self) -> None:
        action = 0
        last_tick = pygame.time.get_ticks()
        self.env.reset()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.env.reset()
                    elif event.key == pygame.K_LEFT:
                        action = 1
                    elif event.key == pygame.K_RIGHT:
                        action = 2
                    elif event.key == pygame.K_UP:
                        action = 3
                    elif event.key == pygame.K_DOWN:
                        action = 4
                    elif event.key == pygame.K_SPACE:
                        action = 5

            now = pygame.time.get_ticks()
            if now - last_tick >= self.tick_ms:
                if not self.env.done:
                    self.env.step(action)
                action = 0
                last_tick = now

            self._draw_board()
            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()


def run_headless_training_demo(episodes: int = 5, max_steps: int = 2000) -> None:
    env = TetrisEnv(seed=42)
    for episode in range(1, episodes + 1):
        state = env.reset()
        total_reward = 0.0
        for _ in range(max_steps):
            action = env.sample_action()
            result = env.step(action)
            state = result.state
            total_reward += result.reward
            if result.done:
                break
        print(
            f"Episode {episode}: score={env.score}, lines={env.lines_cleared}, "
            f"reward={total_reward:.2f}, state_shape={state.shape}"
        )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in {"train", "headless"}:
        run_headless_training_demo()
    else:
        app = TetrisRenderer(TetrisEnv())
        app.run()