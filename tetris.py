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
        self.margin_left = 40
        self.rotation = 0
        self.grid = grid
        self.x = x
        self.block_type = random.choice(self.block_types)

        self.block_indices = []
        self.block_shape = self.get_shapes()
        self.y = y +margin_top+(self.block_height*self.grid_size)
        # hard coding the blocks to check beneath


        self.create_block_list()

    def get_shapes(self):
        if self.block_type=="I":
            self.block_height=0
            if self.rotation==0:
                self.block_width=4
                self.block_indices = [0,1,2,3]
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
            if self.rotation == 0:
                self.block_width = 3
                self.block_indices = [1,2,3]
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
            if self.rotation == 0:
                self.block_width = 2
                self.block_indices = [2,3]
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
            self.block_height=1
            self.block_width=2
            self.block_indices = [2,3]
            return [
                [
                    [1,1],
                    [1,1]
                ]
            ]
        elif self.block_type=="S":
            self.block_height=3
            if self.rotation==0:
                self.block_width=2
                self.block_indices = [3,4]
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
            if self.rotation==0:
                self.block_width=2
                self.block_indices = [0,3,4]
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
            if self.rotation == 0:
                self.block_width = 3
                self.block_indices = [1,2,3]
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

            for j in range(len(self.block_shape[self.rotation][i])):

                if self.block_shape[self.rotation][i][j] == 1:
                    rect_obj = pygame.Rect(self.x+self.grid_size*j,self.y+self.grid_size*i,self.grid_size,self.grid_size)

                    self._blocks.append(rect_obj)


    def control_block(self,move):
        if move == "right":
            if ((self.x-self.margin_left) // self.grid_size)<=len(self.grid[0]) and ((self._blocks[0].x-self.margin_left)+(self.block_width*self.grid_size))//self.grid_size<11:
                if self.grid[(self.y//self.grid_size)-1][(self.x//self.grid_size)] == 0:
                    for rect_obj in self._blocks:
                        self.grid[((rect_obj.y-self.margin_top)//self.grid_size)-1][((rect_obj.x-self.margin_left)//self.grid_size)-1] = 0 #fixes the bug where blocks still remain when block is moved while falling
                        rect_obj.x+=self.grid_size

        if move == "left":
            if ((self.x -self.margin_left)// self.grid_size)>0  and (self._blocks[0].x-self.margin_left)//self.grid_size>1:
                if self.grid[(self.y//self.grid_size)-1][(self.x//self.grid_size)-1] == 0:
                    for rect_obj in self._blocks:
                        self.grid[((rect_obj.y-self.margin_top)//self.grid_size)-1][((rect_obj.x-self.margin_left)//self.grid_size)-1] = 0 #fixes the bug where blocks still remain when block is moved while falling

                        rect_obj.x-=self.grid_size

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
        self.init_block = block(self.grid_size*5,0,self.screen,self.grid_size,self.grid,self.margin_top)
        self.pieces = []
        self.collision_blocks = []
        self.start_time = 0


    def draw_grid(self):
        for i ,col in enumerate(self.grid):
            for j ,cell in enumerate(col):
                if cell == 0:
                    pygame.draw.rect(self.screen, "white", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))
                elif cell == 1:
                    pygame.draw.rect(self.screen, "red", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))
                else:
                    pygame.draw.rect(self.screen, "green", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))


    def check_rows(self):
        for i in range(len(self.grid)-1,-1,-1):
            row = self.grid[i]
            if 0 not in row and 1 not in row:
                self.grid = np.delete(self.grid,i,0)
                self.grid = np.insert(self.grid,[0]*len(self.grid),0,axis=0)
                self.score += 10
                print(f"score: {self.score}")
                break
        pygame.display.set_caption(
            f"Tetris | Score: {self.score}"
        )



    def update_grid(self):
        # block spawner
        if self.init_block is not None:
            self.block_data = self.init_block._blocks

            for rect_obj in self.init_block._blocks:
                if ((rect_obj.y-self.margin_top)//self.grid_size)-1 >=0:
                    if ((rect_obj.y - self.margin_top) // self.grid_size) - 1 < len(self.grid) and ((rect_obj.x - self.margin_left) // self.grid_size) - 1 <= len(self.grid[0]):
                        self.grid[((rect_obj.y - self.margin_top) // self.grid_size) - 1][
                            ((rect_obj.x - self.margin_left) // self.grid_size) - 1] = 1

        else:
            for rect_obj in self.block_data:
                self.grid[((rect_obj.y-self.margin_top)//self.grid_size)-1][((rect_obj.x-self.margin_left)//self.grid_size)-1] = 2

            # game over logic
            self.init_block = block(self.grid_size*5,0,self.screen,self.grid_size,self.grid,self.margin_top)

            for rect_obj in self.init_block._blocks:
                if ((rect_obj.y-self.margin_top)//self.grid_size)-1 >=0:
                    if self.grid[((rect_obj.y-self.margin_top)//self.grid_size)-1][((rect_obj.x-self.margin_left)//self.grid_size)-1] !=0:
                        self.running = False
                        print("Game Over!")
                        break

    def block_move(self):

        if self.init_block is not None:
            self.block_data = self.init_block._blocks
            last_block = self.block_data[-1]
            # checking if the last block has reached the bottom or not
            if (last_block.y-self.margin_top)//self.grid_size<=(self.num_grid_rows)-1 :
                # if the block hasnt reached the bottom we check what's beneath the last piece of the block
                self.move = True
                for i in self.init_block.block_indices:

                    checking_block = self.block_data[i]
                    col = ((checking_block.x -self.margin_left)//self.grid_size)-1
                    row = ((checking_block.y-self.margin_top)//self.grid_size)

                    if row <= len(self.grid):
                        if self.grid[row][col] == 2:
                            self.move = False

                if self.move:
                    for rect_obj in self.block_data:
                        self.grid[((rect_obj.y-self.margin_top)//self.grid_size)-1][((rect_obj.x-self.margin_left)//self.grid_size)-1] = 0
                        rect_obj.y+=self.grid_size
                else:
                    self.init_block = None



            else:
                self.init_block = None

        else:
            self.init_block = block(self.grid_size*5,0,self.screen,self.grid_size,self.grid,self.margin_top)


    def visual_run(self):
        print("mode:visual")
        self.start_time = pygame.time.get_ticks()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        print("the block instance is deleted.")
                        self.init_block = None
                    if event.key == pygame.K_RIGHT:
                        if self.init_block is not None:
                            self.init_block.control_block("right")
                    if event.key == pygame.K_LEFT:
                        if self.init_block is not None:
                            self.init_block.control_block("left")

            self.screen.fill("black")
            self.update_grid()
            self.draw_grid()
            if self.start_time + 250 < pygame.time.get_ticks():
                self.start_time = pygame.time.get_ticks()
                self.block_move()

            pygame.display.update()
            self.check_rows()
            self.clock.tick(self.FPS)


if __name__=="__main__":
    game = game()
    game.visual_run()