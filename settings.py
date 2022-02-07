from pygame.locals import *


class Global:
    # UI
    # block size must be an integer
    BLOCK_SIZE: int = 12
    UI_SCALE: int = 2 * BLOCK_SIZE

    # paddings must be an integer multiple of block size
    TOP_PADDING: int = UI_SCALE
    BOTTOM_PADDING: int = UI_SCALE
    LEFT_PADDING: int = 0
    RIGHT_PADDING: int = 0

    # grid count must be integers
    GRID_COL: int = 80
    GRID_ROW: int = 50

    # do not change this variable
    SCREEN_SIZE: tuple[int] = (GRID_COL * BLOCK_SIZE + LEFT_PADDING + RIGHT_PADDING,
                   GRID_ROW * BLOCK_SIZE + TOP_PADDING + BOTTOM_PADDING)

    # R, G, B
    BACK_GROUND_COLOR: tuple[int] = (31, 59, 100)

    FPS: int = 60

    # snake
    INIT_LENGTH: int = 3

    INIT_HEALTH: int = 8
    MAX_HEALTH: int = 8

    INIT_SATIETY: int = 8
    MAX_SATIETY: int = 8

    INIT_SPEED: int = 4
    MIN_SPEED: int = 1
    MAX_SPEED: int = 20

    MAX_LEVEL: int = 10

    # others
    WALL_MAX_COUNT_IN_THOUSANDTHS: int = 20


class KeyBoard:
    pause_list = {
        K_SPACE, K_ESCAPE, K_p, K_KP_0
    }
    select_list = {
        K_RETURN, K_KP_ENTER
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
