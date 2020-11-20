# Tetris - DYOA Advanced at TU Graz WS 2020
# Name:       Felix Holz
# Student ID: 12027232

import pygame, sys, time, random, math
from pygame.locals import *
from framework import BaseGame


# Recommended Start: init function of Block Class
class Block:
    blocknames = ['clevelandZ', 'rhodeIslandZ', 'blueRicky', 'smashBoy', 'orangeRicky', 'teewee', 'hero']

    def __init__(self, game, block_name):
        # Randomize rotation
        self.game = game
        self.name = block_name
        self.possible_rotations = len(game.block_list[block_name])
        self.rotation = random.randint(0, len(game.block_list[block_name])-1)
        self.set_shape(game.block_list[block_name][self.rotation])
        self.x = int(game.board_width / 2) - int(self.width / 2)
        self.y = 0
        self.color = game.block_colors[block_name]

    def set_shape(self, shape):
        self.shape = shape
        self.width = len(shape[0])
        self.height = len(shape)

    def right_rotation(self, rotation_options):
        if self.possible_rotations == 1: return;
        # rotate block once clockwise
        self.rotation = (self.rotation + 1) % (self.possible_rotations)
        self.set_shape(self.game.block_list[self.name][self.rotation])
        if not self.game.is_block_on_valid_position(self):
            self.left_rotation(0)

    def left_rotation(self, rotation_options):
        if self.possible_rotations == 1: return;
        # rotate block once counter-clockwise
        self.rotation = (self.rotation - 1)
        if self.rotation == -1:
            self.rotation = self.possible_rotations - 1
        self.set_shape(self.game.block_list[self.name][self.rotation])

        if not self.game.is_block_on_valid_position(self):
            self.right_rotation(0)

class Game(BaseGame):
    def __init__(self):
        super(Game, self).__init__()
        self.base_speed = self.speed
        self.level = 0

    def run_game(self):
        print("run_game")
        self.board = self.get_empty_board()
        fall_time = time.time()
        self.paused = False

        current_block = self.get_new_block()
        next_block = self.get_new_block()

        self.score_dictionary = {
            0: 0,
            1: 40,
            2: 100,
            3: 300,
            4: 1200
        }

        # GameLoop
        while True:
            self.test_quit_game()
            for event in pygame.event.get():
                # TODO: Multiple key presses are processed in single loop. good or bad?
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        if self.paused: continue
                        current_block.right_rotation(0)
                    if event.key == pygame.K_q:
                        if self.paused: continue
                        current_block.left_rotation(0)
                    if event.key == pygame.K_LEFT:
                        if self.paused: continue
                        if self.is_block_on_valid_position(current_block, -1, 0):
                            current_block.x -= 1
                    if event.key == pygame.K_RIGHT:
                        if self.paused: continue
                        if self.is_block_on_valid_position(current_block, 1, 0):
                            current_block.x += 1
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if event.key == pygame.K_DOWN:
                        while self.gametick(current_block):
                            pass


            if self.paused:
                self.show_text("Paused")
                self.paused = False  # because show_text blocks until key pressed

            if not self.gametick(current_block):
                self.add_block_to_board(current_block)
                current_block = next_block
                next_block = self.get_new_block()

            if self.is_block_colliding_with_board(current_block):
                self.show_text("Game Over")
                sys.exit()  # because show_text blocks until any key is pressed

            self.speed = self.base_speed + self.level

            # Draw after game logic
            self.display.fill(self.background)
            self.draw_game_board()
            self.draw_score()
            self.draw_level()
            self.draw_next_block(next_block)
            if current_block != None:
                self.draw_block(current_block)
            pygame.display.update()
            self.set_game_speed(self.speed)
            self.clock.tick(self.speed)

    # moves the block by one,
    # returns true if everything went well
    # returns false if block is stuck
    def gametick(self, current_block):
        good_position = True
        if self.is_block_on_valid_position(current_block, 0, 1):
            current_block.y += 1
        else:
            good_position = False

        return good_position

    # Check if Coordinate given is on board (returns True/False)
    def is_coordinate_on_board(self, x, y):
        # check if coordinate is on playingboard (in boundary of self.boardWidth and self.boardHeight)
        if x < 0 or x > (self.board_width-1):
            return False
        if y < 0 or y > (self.board_height-1):
            return False
        return True

    def is_block_colliding_with_board(self, block):
        valid_position = False
        for i in range(0, block.height):
            for j in range(0, block.width):
                if block.shape[i][j] == 'x':
                    if not self.gameboard[block.y + i][block.x + j] == '.':
                        valid_position = True
        return valid_position

    # Parameters block, x_change (any movement done in X direction), yChange (movement in Y direction)
    # Returns True if no part of the block is outside the Board or collides with another Block
    def is_block_on_valid_position(self, block, x_change=0, y_change=0):
        valid_position = True

        for i in range(0, block.height):
            for j in range(0, block.width):
                if block.shape[i][j] == 'x':
                    if not self.is_coordinate_on_board(block.x + x_change + j, block.y + y_change + i):
                        valid_position = False
                    else:
                        if not self.gameboard[block.y + y_change + i][block.x + x_change + j] == '.':
                            valid_position = False
        return valid_position

    # Check if the line on y Coordinate is complete
    # Returns True if the line is complete
    def check_line_complete(self, y_coord):
        row = self.gameboard[y_coord]

        complete = True
        for item in row:
            if item is self.blank_color:
                complete = False
                break

        return complete

    # Go over all lines and remove those, which are complete
    # Returns Number of complete lines removed
    def remove_complete_line(self):
        nr_rows_removed = 0

        for i in range(0, self.board_height):
            if self.check_line_complete(i):
                # self.gameboard.pop(i)

                for j in range(i, 0, -1):
                    self.gameboard[j] = self.gameboard[j-1]

                self.gameboard[0] = ([self.blank_color] * self.board_width)

                nr_rows_removed += 1

        self.calculate_new_score(nr_rows_removed, self.level)
        return nr_rows_removed

    # Create a new random block
    # Returns the newly created Block Class
    def get_new_block(self):
        blockname = random.choice(Block.blocknames)
        block = Block(self, blockname)
        return block

    def add_block_to_board(self, block):
        for i in range(0, block.height):
            for j in range(0, block.width):
                if block.shape[i][j] == 'x':
                    _x = block.y + i
                    _y = block.x + j
                    self.gameboard[_x][_y] = block.color

        self.remove_complete_line()

    # calculate new Score after a line has been removed
    def calculate_new_score(self, lines_removed, level):
        new_points = self.score_dictionary[lines_removed]
        new_points *= (level + 1)
        self.score += new_points
        #print("Score: " + str(self.score))
        self.calculate_new_level(self.score)
        # TODO Maybe call calculate_new_level?
        # Points per lines removed corresponds to the score_directory
        # Points gained: Points per line removed at once times the level modifier!
        # The level
        # modifier is 1 higher than the current level.

    # calculate new Level after the score has changed
    def calculate_new_level(self, score):
        # The level generally corresponds to the score divided by 300 points.
        # 300 -> level 1; 600 -> level 2; 900 -> level 3
        # TODO increase gamespeed by 1 on level up only
        self.level = math.floor(score / 300)

    # set the current game speed
    def set_game_speed(self, speed):
        self.speed = speed
        # set the correct game speed!
        # It starts as defined in base.py and should increase by 1 after a level up.


#-------------------------------------------------------------------------------------
# Do not modify the code below, your implementation should be done above
#-------------------------------------------------------------------------------------
def main():
    pygame.init()
    game = Game()

    game.display = pygame.display.set_mode((game.window_width, game.window_height))
    game.clock = pygame.time.Clock()
    pygame.display.set_caption('Tetris')
    game.show_text('Tetris')
    game.run_game()
    game.show_text('Game Over')


if __name__ == '__main__':
    main()
