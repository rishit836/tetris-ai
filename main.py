import pygame
import os
import sys
import random



class block:
    instances = []
    moving_instance = None
    def __init__(self,x,y,block_type,screen,grid_size,grid):
        self.screen=screen

        self.block_type=block_type
        self.grid_state = grid
        # self.block_type="I"
        self.grid_size = grid_size
        self.instances.append(self)
        self.rotation=0
        self.color= self.get_color()
        self.shapes= self.get_shapes()
        self.x = x
        self.y = y - (self.grid_size*(self.block_height+1))
        self.current_shape=self.shapes[self.rotation]
        self._block = []
        self.moving =True
        self.falling_black = True
        self.block_height = 0
        self.block_width = 0


    def get_color(self):
        if self.block_type=="I":
            return "blue"
        elif self.block_type=="J":
            return "green"
        elif self.block_type=="L":
            return "red"
        elif self.block_type=="O":
            return "yellow"
        elif self.block_type=="S":
            return "purple"
        elif self.block_type=="Z":
            return "orange"
        elif self.block_type=="T":
            return "cyan"
        else:
            return "white"
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

    def draw_piece(self):
        self._block = []
        for i,row in enumerate(self.current_shape):
            for j,col in enumerate(row):
                if col == 1:
                    pygame.draw.rect(self.screen,self.color,pygame.Rect(self.x+(j*self.grid_size),self.y+(i*self.grid_size),self.grid_size,self.grid_size))
                    self._block.append(pygame.Rect(self.x+(j*self.grid_size),self.y+(i*self.grid_size),self.grid_size,self.grid_size))

    def set_move(self):
        for object in self.instances:

            if object == self:
                continue
            else:
                if object.x == self.x and object.y == self.y:
                    print("collision")
                    self.moving = False
                    self.falling_black = False
    def move(self):
        if self.moving and self._block[-1].center[1]<self.grid_size*20:
            self.set_move()
            self.y+=self.grid_size
        else:
            self.moving=False
            self.grid_state=self.update_grid()
            print(self.grid_state)

    def update_grid(self):
        # for r in range(len(self.grid_state)):
        #     for c in range(len(self.grid_state[r])):
        #         if self.grid_state[r][c] == "B":
        #             self.grid_state[r][c] = 0

            # Compute grid indices from pixel x, y and grid_size
        base_row = self.y // self.grid_size
        base_col = self.x // self.grid_size

        # Stamp current shape into the grid as "B"
        for i, row in enumerate(self.current_shape):
            for j, val in enumerate(row):
                if val == 1:
                    gr = base_row + i
                    gc = base_col + j
                    if 0 <= gr < len(self.grid_state) and 0 <= gc < len(self.grid_state[gr]):
                        self.grid_state[gr][gc] = "B"

        return self.grid_state

class block_spawner():
    def __init__(self,grid_size,block_types,screen,grid):
        self.grid_size = grid_size
        self.block_types = block_types
        self.screen = screen
        self.block_type = random.choice(self.block_types)
        self.grid = grid
        self.init_block = block(self.grid_size*4,self.grid_size*1,self.block_type,self.screen,self.grid_size,self.grid)
        self.init_block.draw_piece()
    def update_block(self):
        self.init_block.move()
        self.init_block.draw_piece()


class Game:
    def __init__(self):
        pygame.init()

        self.FPS = 60
        self.score = 0

        self.num_grid_cols= 10
        self.num_grid_rows = 20
        self.margin_left = 40
        self.margin_top = 40
        self.margin_bottom = 10
        self.side_panel_width = 250
        self.grid_size = 40

        self.HEIGHT = (self.grid_size*self.num_grid_rows) + self.margin_top + self.margin_bottom
        self.WIDTH = (self.grid_size*self.num_grid_cols) + self.margin_left +self.side_panel_width
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()

        self.grid = []
        self.create_grid()
        self.pieces = []

    def create_grid(self):
        self.grid=[]
        for column in range(0,self.num_grid_cols):
            column=[]
            for row in range(0,self.num_grid_rows):
                column.append(0)
            self.grid.append(column)

        print("grid created")


    def draw_grid(self):
        for column in range(0,self.num_grid_cols+1):
            for row in range(0,self.num_grid_rows+1):
                pygame.draw.line(self.screen,"white",(self.margin_left,self.margin_top+(self.grid_size*row)),(self.margin_left+(self.grid_size*column),self.margin_top+self.grid_size*row))
                pygame.draw.line(self.screen,"white",(self.margin_left+(self.grid_size*column),self.margin_top),(self.margin_left+(self.grid_size*column),self.margin_top+self.grid_size*self.num_grid_rows))


    def visual_run(self):
        print("mode:visual")
        spawner = block_spawner(self.grid_size,["I","J","L","O","S","Z","T"],self.screen,self.grid)
        while self.running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.running=False
                    sys.exit()
            self.screen.fill("black")
            spawner.update_block()




            # pygame.time.delay(300)


            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(self.FPS)


if __name__=="__main__":
    game = Game()
    Game.visual_run(game)