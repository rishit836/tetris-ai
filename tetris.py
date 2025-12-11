import sys
import random
import numpy as np
import pygame

class block:
    block_types = ["I","J","L","O","S","Z","T"]
    def __init__(self,x,y,screen,grid_size,grid,margin_top,block_type=None):

        self.screen=screen
        self.grid_size = grid_size
        self.margin_top = margin_top
        self.margin_left = 40
        self.rotation = 0
        self.grid = grid
        self.x = x

        if block_type is None:
            self.block_type = random.choice(self.block_types)
        else:
            self.block_type = block_type

        self.block_indices = []
        self.left_most_blocks = []
        self.right_most_blocks = []
        self.block_shape = self.get_shapes()
        self.y = y +margin_top+(self.block_height*self.grid_size)

        self.num_grid_cols = 10
        self.num_grid_rows = 20
        self.computed = False
        self.create_block_list()

    def get_shapes(self):
        if self.block_type=="I":
            self.block_height=0
            if self.rotation==0:
                self.block_width=4
                self.block_indices = [[0,1,2,3],[3]]
            self.right_most_blocks = [3,0]
            self.left_most_blocks = [0,0]
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
                self.block_indices = [[1,2,3],[1,3],[0,1,3]]
            self.right_most_blocks = [3,1,2,0]
            self.left_most_blocks = [1,0,0,3]
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
                self.block_indices = [[2,3],[1,2,3],[0,3],[1,2,3]]
            self.right_most_blocks = [3,2,1,0]
            self.left_most_blocks = [0,0,0,1]
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
            self.block_indices = [[2,3]]
            self.right_most_blocks = [3]
            self.left_most_blocks = [3]
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
                self.block_indices = [[3,4],[1,2,4]]
            self.right_most_blocks = [1,3]
            self.left_most_blocks = [3,0]
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
                self.block_indices = [[0,3,4],[2,3,4]]
            self.right_most_blocks = [4,0]
            self.left_most_blocks = [0,1]
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
                self.block_indices = [[1,2,3],[2,3],[0,2,3],[1,3]]
            self.right_most_blocks = [3,2,2,0]
            self.left_most_blocks = [1,0,0,1]
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
            check_block = self._blocks[self.right_most_blocks[self.rotation]]
            self.movable_right = True
            if ((check_block.x-self.margin_left)//self.grid_size)<len(self.grid[0]):
                if self.grid[((check_block.y-self.margin_top)//self.grid_size)-1][((check_block.x-self.margin_left)//self.grid_size)] == 0:
                    self.movable_right = True
                else:
                    self.movable_right = False
            else:
                self.movable_right = False

            if self.movable_right:
                for rect_obj in self._blocks:
                    self.grid[self.grid == 1] = 0
                    rect_obj.x+=self.grid_size


        if move == "left":
            self.movable_left = True
            check_block = self._blocks[self.left_most_blocks[self.rotation]]
            if ((check_block.x-self.margin_left)//self.grid_size)-2>=0:
                if self.grid[((check_block.y-self.margin_top)//self.grid_size)][((check_block.x-self.margin_left)//self.grid_size)-2] == 0:
                    self.movable_left = True
                else:
                    self.movable_left = False
            else:
                self.movable_left = False

            if self.movable_left:
                for rect_obj in self._blocks:
                    self.grid[self.grid == 1] = 0
                    rect_obj.x-=self.grid_size



    def rotate_block(self):
        self.prev_rotation = self.rotation
        #clamp the rotation to length of the block shape
        # checking for corner cases:
        # right corner:
        right_block = self._blocks[self.right_most_blocks[self.rotation]]
        if (right_block.x -self.margin_left)//self.grid_size == len(self.grid[0]):
            return False
        # left corner:
        left_block = self._blocks[self.left_most_blocks[self.rotation]]
        if (left_block.x -self.margin_left)//self.grid_size == 0:
            return False

        if self.rotation < len(self.block_shape)-1:
            self.rotation+=1
        else:
            self.rotation = 0
        self.y = self._blocks[0].y
        self.x = self._blocks[0].x
        self.prev_y = self.y
        self.prev_x = self.x
        self.create_block_list()

        # checking if the rotation is valid or not
        for rect_obj in self._blocks:
            block_row = ((rect_obj.y-self.margin_top)//self.grid_size)-1
            block_col = ((rect_obj.x-self.margin_left)//self.grid_size)-1

            if (block_row < 0 or block_col < 0 ) or (block_row >= len(self.grid) or block_col >= len(self.grid[0])):
                self.rotation = self.prev_rotation

                self.x = self.prev_x
                self.y = self.prev_y
                self.create_block_list()

                return False
            if not self.grid[block_row][block_col] == 0:
                self.rotation = self.prev_rotation
                self.x = self.prev_x
                self.y = self.prev_y
                self.create_block_list()

                return False

        return True


    def ghost_piece(self):
        offset = 0
        while True:
            collision = False
            for idx in self.block_indices[self.rotation]:
                check_block = self._blocks[idx]

                check_block_x = (((check_block.x - self.margin_left))//self.grid_size) - 1
                check_block_y = (((check_block.y-self.margin_top))//self.grid_size)+(offset+1)

                print(offset)

                if check_block_y >= self.num_grid_rows:
                    collision = True
                    break
                if check_block_y >=0:
                    if self.grid[check_block_y][check_block_x] == 2:
                        collision = True
                        break

            if collision:
                print("calculated the ghost piece")
                break

            offset+= 1
        ghost_rects = []
        for rect in self._blocks:
            ghost_rect = rect.copy()
            ghost_rect.y += (offset*self.grid_size)
            ghost_rect.x -= self.grid_size
            ghost_rects.append(ghost_rect)
        return ghost_rects


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
        self.speed = 350

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
                elif cell == 2:
                    pygame.draw.rect(self.screen, "green", pygame.Rect(self.margin_left + (self.grid_size * j), self.margin_top + (self.grid_size * i), self.grid_size, self.grid_size))


        if self.init_block is not None:
            ghost_rects = self.init_block.ghost_piece()

            for rect in ghost_rects:
                pygame.draw.rect(self.screen,(128,128,128),rect,width=2)



    def check_rows(self):
        non_full_rows = self.grid[~((self.grid == 2).all(axis=1))]
        rows_cleared = self.grid.shape[0] - non_full_rows.shape[0]
        if rows_cleared > 0:
            new_rows = np.zeros((rows_cleared, self.grid.shape[1]))
            self.grid = np.vstack((new_rows, non_full_rows))
            self.speed -= 25
            if not self.speed >0:
                self.speed = 0

            self.score+=100*rows_cleared
            pygame.display.set_caption(
                f"Tetris | Score: {self.score}"
            )
            self.update_grid()

    def update_grid(self):
        # block spawner
        if self.init_block is not None:
            self.block_data = self.init_block._blocks
            self.grid[self.grid==1]=0

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
                for i in self.init_block.block_indices[self.init_block.rotation]:

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
                        self.speed-=25
                        self.score += 100
                        self.update_grid()
                    if event.key == pygame.K_RIGHT:
                        if self.init_block is not None:
                            self.init_block.control_block("right")
                        self.update_grid()

                    if event.key == pygame.K_LEFT:
                        if self.init_block is not None:
                            self.init_block.control_block("left")
                        self.update_grid()


                    if event.key == pygame.K_UP:
                        if self.init_block is not None:
                            self.grid[self.grid == 1] = 0

                        rotation_done = self.init_block.rotate_block()
                        if rotation_done:
                            print("block rotated")
                        else:
                            print("Block cant be rotated")
                        self.update_grid()

                    if event.key == pygame.K_DOWN:
                        if self.init_block !=  None:
                            self.block_move()




            self.screen.fill("black")
            if self.start_time + self.speed < pygame.time.get_ticks():
                self.start_time = pygame.time.get_ticks()
                self.check_rows()
                self.block_move()

            self.update_grid()
            self.draw_grid()

            pygame.display.update()
            self.clock.tick(self.FPS)



if __name__=="__main__":
    game = game()
    game.visual_run()