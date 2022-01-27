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
    GRID_ROW = 1

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
