import pygame


class Global:
    # === UI ===
    # block size must be an integer
    BLOCK_SIZE: int = 12
    UI_SCALE: int = 25

    # paddings must be an integer multiple of block size
    TOP_PADDING: int = UI_SCALE
    BOTTOM_PADDING: int = UI_SCALE
    LEFT_PADDING: int = 0
    RIGHT_PADDING: int = 0

    # grid count must be integers
    GRID_COL: int = 80
    GRID_ROW: int = 50

    # do not change this variable
    SCREEN_SIZE: tuple[int, int] = (GRID_COL * BLOCK_SIZE + LEFT_PADDING + RIGHT_PADDING,
                                    GRID_ROW * BLOCK_SIZE + TOP_PADDING + BOTTOM_PADDING)

    # R, G, B
    BACK_GROUND_COLOR: tuple[int, int, int] = (31, 59, 100)

    FPS: int = 60

    # === snake ===
    INIT_LENGTH: int = 3
    INIT_POS: tuple[int, int] = (10, 2)  # initial position (x, y) of tail

    INIT_HEALTH: int = 8
    MAX_HEALTH: int = 8

    INIT_SATIETY: int = 8
    MAX_SATIETY: int = 8

    INIT_SPEED: int = 4
    MIN_SPEED: int = 1
    MAX_SPEED: int = 1000
    SHOW_REAL_SPEED: bool = False

    MAX_LEVEL: int = 10

    # === others ===
    WALL_COUNT_IN_THOUSANDTHS: int = 20


class KeyBoard:
    pause_list = {
        pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_p, pygame.K_KP_0
    }
    select_list = {
        pygame.K_RETURN, pygame.K_KP_ENTER
    }

    up_list = {
        pygame.K_k, pygame.K_UP, pygame.K_KP8
    }
    down_list = {
        pygame.K_j, pygame.K_DOWN, pygame.K_KP5
    }
    left_list = {
        pygame.K_h, pygame.K_LEFT, pygame.K_KP4
    }
    right_list = {
        pygame.K_l, pygame.K_RIGHT, pygame.K_KP6
    }

    quit_game_list = {
        pygame.K_q, pygame.K_ESCAPE
    }
