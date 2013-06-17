# snake.py
# a snake game
# Copyright (c) 2013 Skyler Riske

import random
import pygame
from pygame.locals import *

# direction constants
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

# color(s)
yellow = (255, 255, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)


class Game:

    def __init__(self):
        pygame.init()
        self.FPS = 18
        self.clock = pygame.time.Clock()
        self.WIN_WIDTH = 640
        self.WIN_HEIGHT = 480
        self.screen = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.running = True
        self.pausing = False

        # set our title
        pygame.display.set_caption("Snake!")

        # if the game is fullscreen or not
        self.is_fullscreen = False
        pygame.key.set_repeat(1, 2)

        # the current direction of the snake
        self.direction = RIGHT

        # whether or not we have wall collisions
        self.walls = False
        # whether or not the snake wraps around the walls
        self.wrap_walls = True
        # whether or not we should write the score to highscores.txt
        # when the player dies
        self.write_to_highscore = False

        # the width/height of a segment of our snake
        self.SNAKE_SEGMENT_WIDTH = 16  # 16px
        # the size of the food is the same as the size of a segment of the snake
        self.FOOD_WIDTH = self.SNAKE_SEGMENT_WIDTH
        # the initial length of our snake
        self.INIT_SNAKE_LENGTH = 5

        # whether the snake is dead or not
        self.snake_is_dead = False

        self.create_snake()

        # initialize our score counter
        self.score_counter = ScoreCounter()

        self.end_screen_is_showing = True

        self.create_food()
        self.eating_food = False


    def start_game_loop(self):
        """Start the game loop"""

        while self.running:
            # clear our screen with black
            self.screen.fill((0, 0, 0))

            if self.snake_is_dead != True:
                # if the game is paused, the snake should theoretically
                # not be moving
                if not self.pausing:
                    self.move_snake()
                self.draw_snake()
                self.draw_food()
                self.draw_scoreboard()

                self.check_for_head_colliding_with_body()
                self.check_if_eating_food()

                self.check_for_wall()

                # if the snake has just been killed, initialize the
                # end screen resources before the if statement is no
                # longer true.
                if self.snake_is_dead:
                    self.init_end_screen_resources()

            # check for events
            self.check_for_events()

            if self.snake_is_dead:
                self.draw_end_screen()

            self.clock.tick(self.FPS)
            # update our screen
            pygame.display.flip()

        pygame.quit()

    def check_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                # changing the direction of the snake.
                # This also makes sure the snake can't go backwards from its current direction.
                # we can also only change the direction if the game isn't paused
                # possibly move ^ to a higher if statement
                if not self.pausing:
                    if event.key == K_UP and self.direction != DOWN:
                        self.direction = UP
                    elif event.key == K_DOWN and self.direction != UP:
                        self.direction = DOWN
                    if event.key == K_LEFT and self.direction != RIGHT:
                        self.direction = LEFT
                    elif event.key == K_RIGHT and self.direction != LEFT:
                        self.direction = RIGHT

                # pressing shift+k will kill the snake for debug purposes
                if event.key == K_k:
                    if event.mod & KMOD_SHIFT:
                        self.kill_snake()

                elif event.key == K_RIGHTBRACKET:
                    self.SNAKE_SEGMENT_WIDTH += 1

                elif event.key == K_RETURN and self.end_screen_is_showing:
                    # restart the game
                    self.restart_game()

                elif event.key == K_p:
                    # pause or unpause the game
                    if self.pausing is False:
                        self.pausing = True
                    elif self.pausing is True:
                        self.pausing = False

                elif event.key == K_F11:
                    # disable fullscreen if it's on
                    if self.is_fullscreen:
                        # reset the WIN_WIDTH and WIN_HEIGHT variables to
                        # normal window_size
                        self.WIN_WIDTH = 640
                        self.WIN_HEIGHT = 480
                        pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
                        self.is_fullscreen = False
                        # relocate the food so it is now within the regular
                        # window size
                        self.relocate_food()

                    # otherwise enable it
                    else:
                        # add a way to find the size of the user's monitor
                        # and set that to the fullscreen size
                        # also: add default resolution variables and
                        # fullscreen resolution variables

                        # the largest resolution available
                        pygame.display.set_mode(pygame.display.list_modes()[0], pygame.FULLSCREEN)
                        # since we're now at 1080p, set the WIN_WIDTH and WIN_HEIGHT
                        # variables accordingly so everything works properly
                        self.WIN_WIDTH, self.WIN_HEIGHT = pygame.display.list_modes()[0]
                        self.is_fullscreen = True

    def create_snake(self):
        self.snake = []
        # create all the segments of the snake, and start with only the head showing at the top-left corner of the screen
        for i in range(self.INIT_SNAKE_LENGTH):
            self.snake.append(pygame.Rect(i * self.SNAKE_SEGMENT_WIDTH - ((self.INIT_SNAKE_LENGTH - 1) * self.SNAKE_SEGMENT_WIDTH), 0, self.SNAKE_SEGMENT_WIDTH, self.SNAKE_SEGMENT_WIDTH))

    def move_snake(self):
        if self.direction == UP:
            front_snake_block = self.snake[-1]
            if self.eating_food is not True:
                last_snake_block = self.snake.pop(0)  # remove the last snake block
            else:
                self.eating_food = False # make it false so we don't leave anymore blocks at the end
            # insert a new snake block at the front with new coords
            self.snake.append(pygame.Rect(front_snake_block.x, front_snake_block.y - front_snake_block.width, self.SNAKE_SEGMENT_WIDTH, self.SNAKE_SEGMENT_WIDTH))

        elif self.direction == DOWN:
            front_snake_block = self.snake[-1]
            if self.eating_food is not True:
                last_snake_block = self.snake.pop(0)  # remove the last snake block
            else:
                self.eating_food = False # make it false so we don't leave anymore blocks at the end
            # insert a new snake block at the front with new coords
            self.snake.append(pygame.Rect(front_snake_block.x, front_snake_block.y + front_snake_block.width, self.SNAKE_SEGMENT_WIDTH, self.SNAKE_SEGMENT_WIDTH))

        elif self.direction == LEFT:
            front_snake_block = self.snake[-1]
            if self.eating_food is not True:
                last_snake_block = self.snake.pop(0)  # remove the last snake block
            else:
                self.eating_food = False # make it false so we don't leave anymore blocks at the end
            # insert a new snake block at the front with new coords
            self.snake.append(pygame.Rect(front_snake_block.x - front_snake_block.width, front_snake_block.y, self.SNAKE_SEGMENT_WIDTH, self.SNAKE_SEGMENT_WIDTH))

        elif self.direction == RIGHT:
            front_snake_block = self.snake[-1]
            if self.eating_food is not True:
                last_snake_block = self.snake.pop(0)  # remove the last snake block
            else:
                self.eating_food = False # make it false so we don't leave anymore blocks at the end
            # insert a new snake block at the front with new coords
            self.snake.append(pygame.Rect(front_snake_block.x + front_snake_block.width, front_snake_block.y, self.SNAKE_SEGMENT_WIDTH, self.SNAKE_SEGMENT_WIDTH))

    def draw_snake(self):
        color_var = 255
        for block in self.snake:
            # the -2 when specifying the width and height of the block seperates the blocks
            pygame.draw.rect(self.screen, (245, 245, 220), (block.x, block.y, block.width - 1, block.height - 1))
            # this controls the snake's nice gradient color, the gradient works for any length of snake, be it 10 or 40 blocks long :D.
            color_var -= int(color_var / len(self.snake))

    def kill_snake(self):
        self.snake_is_dead = True
        print("the snake has been killed")
        print("you died with {0} points".format(self.score_counter.points))
        if self.write_to_highscore:
            self.score_counter.write_points_to_file()
        self.init_end_screen_resources()

    def check_for_wall(self):
        # """If enabled, check if the head of the snake is touching a wall, if so, kill the snake"""
        # if enabled, check if the snake is touching a wall
        if self.walls:
            head = self.snake[-1]
            # if self.wrap_walls is True, the snake won't die if it hits a wall.
            if self.wrap_walls:
                if head.x < 0:
                    head.x = self.WIN_WIDTH
                elif head.x > self.WIN_WIDTH:
                    head.x = 0
                elif head.y < 0:
                    head.y = self.WIN_HEIGHT
                elif head.y > self.WIN_HEIGHT:
                    head.y = 0
            else:
                # If self.wrap_walls is not enabled, the snake will die
                # if it hits the wall.
                if head.x < 0 or head.x > self.WIN_WIDTH or head.y < 0 or head.y > self.WIN_HEIGHT:
                    self.kill_snake()

    def check_for_head_colliding_with_body(self):
        """Check if the head collides with the snake's body"""
        for i in range(0, len(self.snake)-1):
            # if the head overlaps any part of the snake's body (besides the head) it dies.
            if self.snake[-1].colliderect(self.snake[i]):
                self.kill_snake()

    def create_food(self):
        self.food_item = pygame.Rect(random.randrange(0, self.WIN_WIDTH - self.SNAKE_SEGMENT_WIDTH, self.SNAKE_SEGMENT_WIDTH), random.randrange(0, self.WIN_HEIGHT - self.SNAKE_SEGMENT_WIDTH, self.SNAKE_SEGMENT_WIDTH), self.FOOD_WIDTH - 1, self.FOOD_WIDTH - 1)

    def draw_food(self):
        # draw the food
        pygame.draw.rect(self.screen, blue, self.food_item)

    def check_if_eating_food(self):
        """Check if the head touches the food item"""
        if self.snake[-1].colliderect(self.food_item):
            # the snake has eaten the food, add some points and relocate the food.
            self.score_counter.add_points()
            self.relocate_food()
            self.eating_food = True # this will extend the snake by one segment

    def relocate_food(self):
        self.food_item = pygame.Rect(random.randrange(0, self.WIN_WIDTH - self.SNAKE_SEGMENT_WIDTH, self.FOOD_WIDTH), random.randrange(0, self.WIN_HEIGHT - self.SNAKE_SEGMENT_WIDTH, self.FOOD_WIDTH), self.FOOD_WIDTH - 1, self.FOOD_WIDTH - 1)
        self.food_choice_index = random.randrange(0, 2) # possibly make it a different kind of food

    def draw_scoreboard(self):
        """Draw the score counter"""
        self.screen.blit(self.score_counter.score_text, self.score_counter.score_text_pos)

    def restart_game(self):
        """restart the game by reseting a bunch of variables"""
        print("restarting the game!")
        self.end_screen_is_showing = False
        self.snake_is_dead = False
        self.SNAKE_SEGMENT_WIDTH = 16  # reset the snake's size

        self.create_snake()
        self.score_counter = ScoreCounter()
        self.create_food()
        self.direction = RIGHT

    def init_end_screen_resources(self):
        """ll the player what score they had when they died, and give them
        options to play again or exit.
        """
        self.end_loop_running = True
        self.end_screen_font = pygame.font.Font(None, 30)

        self.end_score_text = self.end_screen_font.render("You died with " + str(self.score_counter.points) + " points", 1, (255, 255, 0))
        self.end_score_text_pos = self.end_score_text.get_rect(centery=(self.WIN_HEIGHT/2) - 20, centerx=self.WIN_WIDTH/2)

        self.end_score_option_text = self.end_screen_font.render("press enter to restart", 1, (255, 255, 255))
        self.end_score_option_text_pos = self.end_score_option_text.get_rect(centery=(self.WIN_HEIGHT/2) + 50, centerx=self.WIN_WIDTH/2 + 2)

        self.end_score_option_text2 = self.end_screen_font.render("press ESC to exit", 1, (255, 255, 255))
        self.end_score_option_text2_pos = self.end_score_option_text.get_rect(centery=(self.WIN_HEIGHT/2) + 80, centerx=self.WIN_WIDTH/2 + 15)

        self.end_screen_is_showing = True

    def draw_end_screen(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.WIN_WIDTH, self.WIN_HEIGHT))
        self.screen.blit(self.end_score_text, self.end_score_text_pos)
        self.screen.blit(self.end_score_option_text, self.end_score_option_text_pos)
        self.screen.blit(self.end_score_option_text2, self.end_score_option_text2_pos)


class ScoreCounter:
    """The ScoreCounter will keep track of the points the snakes receives from eating food"""

    def __init__(self):
        self.points = 0
        self.points_per_food = 5

        self.font = pygame.font.Font(None, 24)
        self.score_text = self.font.render("Score: " + str(self.points), 1, yellow)
        self.score_text_pos = self.score_text.get_rect(x=10, y=5)

    def add_points(self):
        self.points += self.points_per_food
        self.update_score_text()

    def update_score_text(self):
        self.score_text = self.font.render("Score: " + str(self.points), 1, yellow)

    def write_points_to_file(self):
        """Write the user's points to the highscores.txt file"""
        print('debug')
        highscores = open("highscores.txt", "a+")
        highscores.write(str(self.points) + "\n")
        highscores.close()


class Food(pygame.Rect):

    def __init__():
        pass
        # color

        # position

        # size

    # draw

    # update


def main():
    game = Game()
    game.start_game_loop()

if __name__ == '__main__':
    main()
