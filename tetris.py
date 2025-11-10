import sys
import random
import numpy as np
import pygame



class block:
    block_types = ["I","J","L","O","S","Z","T"]
    def __init__(self,x,y,screen,grid_size,grid):
        self.screen=screen
        self.x,self.y = x,y
        self.grid_size = grid_size
        self.grid = grid
        self.block_type = random.choice(self.block_types)
        self.block_shape = self.get_shapes()

    def get_shapes(self):
        if self.block_type=="I":
            self.block_height=0
            return [
                [[0,0,0,0],
                [0,0,0,0],
                [1,1,1,1],
                [0,0,0,0]],

                [[0,0,1,0],
                 [0,0,1,0],
                 [0,0,1,0],
                 [0,0,1,0]]
            ]
        elif self.block_type=="J":
            self.block_height=2
            return [
                [
                    [1,0,0],
                    [1,1,1],
                    [0,0,0]
                 ],
                [
                    [0, 1, 1],
                    [0, 1, 0],
                    [0, 1, 0]
                ],
                [
                    [0, 0, 0],
                    [1, 1, 1],
                    [0, 0, 1]
                ]
                ,
                [[0,1,0],
                 [0,1,0],
                 [1,1,0]],
            ]
        elif self.block_type=="L":
            self.block_height=3
            return [
                [
                    [0,1,0],
                    [0,1,0],
                    [0,1,1]
                ],
                [
                    [0,0,0],
                    [1,1,1],
                    [1,0,0]
                ],
                [
                    [1, 1, 0],
                    [0, 1, 0],
                    [0, 1, 0]
                ],
                [
                    [0, 0, 1],
                    [1, 1, 1],
                    [0, 0, 0]
                ],
            ]
        elif self.block_type=="O":
            self.block_height=2
            return [
                [
                    [1,1],
                    [1,1]
                ]
            ]
        elif self.block_type=="S":
            self.block_height=3
            return [
                [[0,1,1],
                 [0,1,0],
                 [1,1,0]],
                [[1, 0, 0],
                 [1, 1, 1],
                 [0, 0, 1]],
            ]
        elif self.block_type=="Z":
            self.block_height=3
            return [
                [[1,1,0],
                 [0,1,0],
                 [0,1,1]],
                [[0, 0, 1],
                 [1, 1, 1],
                 [1, 0, 0]]
            ]
        elif self.block_type=="T":
            self.block_height=2
            return [
                [[0, 1, 0],
                 [1, 1, 1],
                 [0, 0, 0]],
                [[0, 1, 0],
                 [0, 1, 1],
                 [0, 1, 0]],
                [[0, 0, 0],
                 [1, 1, 1],
                 [0, 1, 0]],
                [[0, 1, 0],
                 [1, 1, 0],
                 [0, 1, 0]],
            ]

class game:
    def __init__(self):
        self.FPS = 60
        self.score = 0

        self.num_grid_cols = 10
        self.num_grid_rows = 20
        self.margin_left = 40
        self.margin_top = 40
        self.margin_bottom = 10
        self.side_panel_width = 250
        self.grid_size = 40

        self.HEIGHT = (self.grid_size * self.num_grid_rows) + self.margin_top + self.margin_bottom
        self.WIDTH = (self.grid_size * self.num_grid_cols) + self.margin_left + self.side_panel_width
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()

        self.grid = np.zeros((self.num_grid_rows,self.num_grid_cols))
        self.pieces = []

    def draw_grid(self):
        for i ,col in enumerate(self.grid):
            for j ,cell in enumerate(col):
                if cell == 0:
                    pygame.draw.rect(self.screen, "white", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))
                else:
                    pygame.draw.rect(self.screen, "red", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))



    def visual_run(self):
        print("mode:visual")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
            self.screen.fill("black")
            self.draw_grid()
            pygame.display.update()
            self.clock.tick(self.FPS)

if __name__=="__main__":
    game = game()
    game.visual_run()