from pygame.locals import *


class Global:
    # UI
    # block size must be an integer
    BLOCK_SIZE = 12
    UI_SCALE = 2 * BLOCK_SIZE

    # paddings must be an integer multiple of block size
    TOP_PADDING = UI_SCALE
    BOTTOM_PADDING = UI_SCALE
    LEFT_PADDING = 0
    RIGHT_PADDING = 0

    # grid count must be integers
    GRID_COL = 80
    GRID_ROW = 50

    # do not change this variable
    SCREEN_SIZE = (GRID_COL * BLOCK_SIZE + LEFT_PADDING + RIGHT_PADDING,
                   GRID_ROW * BLOCK_SIZE + TOP_PADDING + BOTTOM_PADDING)

    # R, G, B
    BACK_GROUND_COLOR = (31, 59, 100)

    FPS = 60

    # snake
    INIT_LENGTH = 3

    INIT_HEALTH = 8
    MAX_HEALTH = 8

    INIT_SATIETY = 8
    MAX_SATIETY = 8

    INIT_SPEED = 4
    MIN_SPEED = 1
    MAX_SPEED = 8

    # others
    WALL_MAX_COUNT_IN_THOUSANDTHS = 20


class KeyBoard:
    pause_list = {
        K_SPACE, K_ESCAPE, K_p
    }
    select_list = {
        K_RETURN,
    }

    up_list = {
        K_k, K_UP, K_KP8
    }
    down_list = {
        K_j, K_DOWN, K_KP5
    }
    left_list = {
        K_h, K_LEFT, K_KP4
    }
    right_list = {
        K_l, K_RIGHT, K_KP6
    }

    quit_game_list = {
        K_q, K_ESCAPE
    }
