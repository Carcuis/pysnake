import pygame
from settings import *


class Snake:
    def __init__(self, parent_screen, parent_game):
        self.parent_screen = parent_screen
        self.parent_game = parent_game

        self.head_block = pygame.image.load("resources/imgs/yellow-fdd926-10x10.png").convert()
        self.head_block = pygame.transform.scale(self.head_block, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.body_block = pygame.image.load("resources/imgs/green-23d12f-10x10.png").convert()
        self.body_block = pygame.transform.scale(self.body_block, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))

        self.init_length = Global.INIT_LENGTH
        self.length = self.init_length
        self.x = [10 * Global.BLOCK_SIZE + Global.BLOCK_SIZE * (self.length - i - 1) for i in range(self.length)]
        self.y = [2 * Global.BLOCK_SIZE] * self.length

        self.move_lock = False
        self.move_speed = Global.INIT_SPEED
        self.direction = "right"
        self.direction_lock = False
        self.buffer_direction = ""
        self.change_direction_buffer_status = False

    def draw(self):
        self.parent_screen.blit(self.head_block, (self.x[0], self.y[0]))
        for i in range(1, self.length):
            self.parent_screen.blit(self.body_block, (self.x[i], self.y[i]))

    def change_direction(self, direction):
        if self.direction_lock:
            self.buffer_direction = direction
            self.change_direction_buffer_status = True
            return

        if self.direction == direction:
            return

        self.direction_lock = True
        if direction == "left" and self.direction != "right":
            self.direction = "left"
        if direction == "right" and self.direction != "left":
            self.direction = "right"
        if direction == "up" and self.direction != "down":
            self.direction = "up"
        if direction == "down" and self.direction != "up":
            self.direction = "down"

    def walk(self):
        # move delay
        if self.parent_game.tick_count < Global.FPS / (3 * self.move_speed - 2):
            self.move_lock = True
            return
        self.parent_game.tick_count = 0

        # move body from tail to neck
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # move head
        step = Global.BLOCK_SIZE
        if self.direction == "left":
            self.x[0] -= step
        elif self.direction == "right":
            self.x[0] += step
        elif self.direction == "up":
            self.y[0] -= step
        elif self.direction == "down":
            self.y[0] += step
        # teleport head if is over border after movement
        over_border, directory = self.head_over_border()
        if over_border:
            self.teleport(directory)

        # unlock locks after actually walk
        self.move_lock = False
        self.direction_lock = False

        # execute buffer mode changing direction if buffer mode is set
        if self.change_direction_buffer_status:
            self.change_direction(self.buffer_direction)
            self.change_direction_buffer_status = False

        self.parent_game.hungry.hungry_step_count += 1

    def head_over_border(self):
        """
        :return: (bool: over_border, int: directory: 0->None 1->left 2->right 3->top 4->bottom)
        """
        if self.x[0] < Global.LEFT_PADDING:
            return True, 1
        if self.x[0] >= Global.SCREEN_SIZE[0] - Global.RIGHT_PADDING:
            return True, 2
        if self.y[0] < Global.TOP_PADDING:
            return True, 3
        if self.y[0] >= Global.SCREEN_SIZE[1] - Global.BOTTOM_PADDING:
            return True, 4
        return False, 0

    def teleport(self, directory):
        if directory == 0:
            return

        if directory == 1:
            # to right
            self.x[0] = Global.SCREEN_SIZE[0] - Global.BLOCK_SIZE - Global.RIGHT_PADDING
        elif directory == 2:
            # to left
            self.x[0] = Global.LEFT_PADDING
        elif directory == 3:
            # to bottom
            self.y[0] = Global.SCREEN_SIZE[1] - Global.BLOCK_SIZE - Global.BOTTOM_PADDING
        elif directory == 4:
            # to top
            self.y[0] = Global.TOP_PADDING

    def increase_length(self, length):
        if length < 0:
            return
        self.length += length
        for i in range(length):
            self.x.append(self.x[-1])
            self.y.append(self.y[-1])

    def increase_speed(self, speed):
        # filter: [1, +inf)
        self.move_speed = max(1, self.move_speed + speed)

    def reset(self):
        self.init_length = Global.INIT_LENGTH
        self.length = self.init_length
        self.x = [10 * Global.BLOCK_SIZE + Global.BLOCK_SIZE * (self.length - i - 1) for i in range(self.length)]
        self.y = [2 * Global.BLOCK_SIZE] * self.length

        self.move_lock = False
        self.move_speed = Global.INIT_SPEED
        self.direction = "right"
        self.direction_lock = False
        self.buffer_direction = ""
        self.change_direction_buffer_status = False
