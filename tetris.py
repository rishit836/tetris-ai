import sys
import random
import numpy as np
import pygame



class block:
    block_types = ["I","J","L","O","S","Z","T"]
    def __init__(self,x,y,screen,grid_size,grid,margin_top):

        self.screen=screen
        self.grid_size = grid_size
        self.margin_top = margin_top
        self.block_type = random.choice(self.block_types)
        self.block_shape = self.get_shapes()
        self.grid = grid
        self.x = x
        self.y = y +margin_top
        print("DEBUG:::",y,self.y)
        self.rotation = 0
        self.create_block_list()

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
        if self.block_type=="J":
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

    def create_block_list(self):
        self._blocks = []
        for i in range(len(self.block_shape[self.rotation])):
            # print(self.block_shape[self.rotation][i])
            for j in range(len(self.block_shape[self.rotation][i])):
                # print(self.block_shape[self.rotation][i][j])
                if self.block_shape[self.rotation][i][j] == 1:
                    rect_obj = pygame.Rect(self.x+self.grid_size*j,self.y+self.grid_size*i,self.grid_size,self.grid_size)
                    print(i)
                    self._blocks.append(rect_obj)
        print(self._blocks)
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
        self.init_block = block(self.grid_size*3,0,self.screen,self.grid_size,self.grid,self.margin_top)
        self.pieces = []

    def draw_grid(self):
        for i ,col in enumerate(self.grid):
            for j ,cell in enumerate(col):
                if cell == 0:
                    pygame.draw.rect(self.screen, "white", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))
                else:
                    pygame.draw.rect(self.screen, "red", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))


    def update_grid(self):
        """
        TODO:
        1)BLOCK SPAWNER
        2)PLACE THE BLOCK IN THE GRID WHEN SPAWNED BASED ON X AND Y
        3)THE BLOCK IF ROTATED THEN SAME SHOULD BE HIGHLIGHTED IN THE GRID
        3)BLOCK SHOULD STOP IF THERE IS A COLLISION
        """

        # block spawner
        if self.init_block is not None:
            for rect_obj in self.init_block._blocks:
                self.grid[(rect_obj.y//self.grid_size)-1][(rect_obj.x//self.grid_size)-1] = 1



    def visual_run(self):
        print("mode:visual")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
            self.screen.fill("black")
            self.draw_grid()
            self.update_grid()
            for rect_obj in self.init_block._blocks:
                # pygame.draw.rect(self.screen, "red", rect_obj, self.grid_size, 1, 1, 1, 1, 1)
                print(rect_obj.x//self.grid_size,rect_obj.y//self.grid_size)
            pygame.display.update()
            self.clock.tick(self.FPS)

if __name__=="__main__":
    game = game()
    game.visual_run()