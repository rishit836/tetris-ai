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
        self.rotation = 0
        self.grid = grid
        self.x = x
        self.y = y +margin_top
        # self.block_type = random.choice(self.block_types)
        self.block_type = "L"
        self.block_shape = self.get_shapes()


        self.create_block_list()

    def get_shapes(self):
        if self.block_type=="I":
            self.block_height=0
            if self.rotation==0:
                self.block_width=4
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
            self.block_width=2
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
            if (self.x // self.grid_size)<len(self.grid[0]) and self._blocks[0].x+(self.block_width*self.grid_size)<self.grid_size*11:
                if self.grid[(self.y//self.grid_size)-1][(self.x//self.grid_size)] == 0:
                    for rect_obj in self._blocks:
                        self.grid[(rect_obj.y//self.grid_size)-1][(rect_obj.x//self.grid_size)-1] = 0 #fixes the bug where blocks still remain when block is moved while falling
                        rect_obj.x+=self.grid_size

        if move == "left":
            if (self.x // self.grid_size)>0  and self._blocks[0].x//self.grid_size>1:
                if self.grid[(self.y//self.grid_size)-1][(self.x//self.grid_size)-1] == 0:
                    for rect_obj in self._blocks:
                        self.grid[(rect_obj.y//self.grid_size)-1][(rect_obj.x//self.grid_size)-1] = 0 #fixes the bug where blocks still remain when block is moved while falling

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
        self.expensive_checking_piece = ["Z","S"]

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
                if (rect_obj.y // self.grid_size) - 1 < len(self.grid) and (rect_obj.x // self.grid_size) - 1 < len(self.grid[0]):

                    self.grid[(rect_obj.y//self.grid_size)-1][(rect_obj.x//self.grid_size)-1] = 1
        else:
            for rect_obj in self.block_data:
                self.grid[(rect_obj.y//self.grid_size)-1][(rect_obj.x//self.grid_size)-1] = 2

            # game over logic
            self.init_block = block(self.grid_size*5,0,self.screen,self.grid_size,self.grid,self.margin_top)

            for rect_obj in self.init_block._blocks:
                if self.grid[(rect_obj.y//self.grid_size)-1][(rect_obj.x//self.grid_size)-1] !=0:
                    self.running = False
                    print("Game Over!")

    def block_move(self):

        if self.init_block is not None:
            self.block_data = self.init_block._blocks
            last_block = self.block_data[-1]
            print("new block data collected")


            # checking if the last block has reached the bottom or not
            if last_block.y//self.grid_size<=(self.num_grid_rows-1) :
                # if the block hasnt reached the bottom we check what's beneath the last piece of the block
                for rect_obj in self.block_data:
                    # checking if the index in the range or not
                    if (rect_obj.y//self.grid_size) -1< len(self.grid):
                        if last_block.y//self.grid_size<len(self.grid):
                            # row beneath the last block of the active/falling piece
                            if (last_block.x//self.grid_size)-(self.init_block.block_width+1) <=0:
                                first_index = (last_block.x // self.grid_size) - self.init_block.block_width
                                last_index = self.init_block.block_width+1

                            else:
                                first_index = (last_block.x//self.grid_size)
                                last_index = (last_block.x//self.grid_size)-(self.init_block.block_width)+1

                            if last_index>first_index:
                                iterator = 1
                            else:
                                iterator = -1
                            print(np.flip(self.grid[(last_block.y//self.grid_size)][first_index:last_index-1:iterator]))
                            print(first_index,last_index)
                            # checking if the row beneath has a block already placed or not
                            if 2 not in self.grid[(last_block.y//self.grid_size)][first_index:last_index:iterator]:
                                # reset the grid behind the block after it has fallen
                                self.grid[(rect_obj.y//self.grid_size)-1][(rect_obj.x//self.grid_size)-1] = 0
                                # move the blocks down
                                rect_obj.y+=self.grid_size
                                # print("no collision detected",self.grid[(last_block.y//self.grid_size)][first_index:last_index:iterator])
                            else:
                                print("block beneath")
                                self.init_block = None
                                break
                        else:
                            # reset the grid behind the block after it has fallen
                            self.grid[(rect_obj.y // self.grid_size) - 1][(rect_obj.x // self.grid_size) - 1] = 0
                            # move the blocks down
                            rect_obj.y += self.grid_size
            else:
                self.init_block = None


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