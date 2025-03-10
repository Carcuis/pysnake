import getpass
import time
from collections import deque
from threading import Event, Thread

import pygame

from animation import AnimationManager
from board import Board, Button, Text
from event import EventManager
from food import FoodManager
from grid import Grid
from settings import Global, KeyBoard
from snake import Direction, Snake
from util import Action, GameState, Util
from wall import Wall


class Game:
    def __init__(self) -> None:
        pygame.display.set_caption("PySnake")
        pygame.display.set_icon(pygame.image.load("resources/img/icon.png"))
        self.surface = pygame.display.set_mode(Global.SCREEN_SIZE, pygame.RESIZABLE)
        self.banner_img = pygame.transform.rotozoom(
            pygame.image.load("resources/img/banner.png").convert_alpha(),
            0, Global.SCREEN_SIZE[0] * 0.001
        )
        self.clock = pygame.time.Clock()

        self.grid = Grid(Global.GRID_COL, Global.GRID_ROW)
        self.animation_manager = AnimationManager(self.grid)
        self.snake = Snake(self.grid)
        self.wall = Wall(self.grid)
        self.food_manager = FoodManager(self.grid, self.surface)
        self.board = Board()
        self.snake_move_timer = Util.timer()

        self.level: int = 1
        self.score: int = 0
        self.move_distance: int = 0
        self.eat_food_count: int = 0

        if Global.SHOW_REAL_SPEED:
            self.head_deque: deque = deque(maxlen=5)  # store head positions of snake, used to calculate real_speed
            self.real_speed: int = 0
            self.calc_speed_running = Event()
            Thread(target=self.calc_real_speed, daemon=True).start()

    def reset_game(self) -> None:
        self.grid.clear_all()
        self.snake.reset()
        self.wall.reset()
        self.food_manager.reset()
        self.snake.health.reset()
        self.snake.hungry.reset()
        self.level = 1
        self.score = 0
        self.move_distance = 0
        self.eat_food_count = 0
        if Global.SHOW_REAL_SPEED:
            self.calc_speed_running.clear()
            self.head_deque.clear()
            self.real_speed = 0

    def main_menu(self) -> Action:
        self.animation_manager.start()

        start_button = Button(
            title="Start", color=(pygame.Color("white"), pygame.Color("green")), position=(0.5, 0.65)
        )
        exit_button = Button(
            title="Exit game", color=(pygame.Color("white"), pygame.Color("red")), position=(0.5, 0.85)
        )

        self.board.add(start_button, exit_button)

        while True:
            EventManager.get_event()
            self.board.update_button_status()
            self.animation_manager.update()

            self.set_base_color(Global.BACK_GROUND_COLOR)
            self.animation_manager.draw(self.surface)
            self.draw_banner()

            self.board.draw(self.surface)

            if start_button.is_triggered:
                self.animation_manager.pause()
                self.board.clear_button()
                return Action.START_GAME

            if exit_button.is_triggered:
                return Action.QUIT_GAME

            Util.update_screen()
            self.clock.tick(Global.FPS)

    def start_game(self) -> tuple[Action, GameState]:
        self.snake_move_timer.set_interval_sec(1 / (1.5 * self.snake.move_speed))
        self.snake_move_timer.start()
        if Global.SHOW_REAL_SPEED:
            self.calc_speed_running.set()
        self.init_game_surface()

        while True:
            EventManager.get_event()

            alive, result, _, _, _ = self.play(teleport=Global.TELEPORT)
            speed = f"{self.snake.move_speed} [{self.real_speed} bps]" if Global.SHOW_REAL_SPEED else self.snake.move_speed
            self.board.add(
                Text(f"FPS: {round(self.clock.get_fps())}", pygame.Color("white"), "left_top", alpha=255),
                Text(f"score: {self.get_score()}  len: {self.snake.length}",
                     pygame.Color("springgreen"), "right_top", alpha=255),
                Text(f"speed: {speed}", pygame.Color("white"), "middle_top", alpha=255),
                Text(f"level: {self.level}", pygame.Color("chartreuse"), "middle_bottom", alpha=255)
            )
            self.update_board()
            Util.update_screen()

            if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.pause_list) or \
                    EventManager.check_key_or_button(pygame.MOUSEBUTTONDOWN, 3):
                # enter pause menu
                self.snake_move_timer.pause()
                if Global.SHOW_REAL_SPEED:
                    self.calc_speed_running.clear()
                    self.head_deque.clear()

                next_action = self.pause()
                if next_action in {Action.START_GAME, Action.MAIN_MENU}:
                    return next_action, result
                if next_action == Action.CONTINUE:
                    self.snake_move_timer.start()
                    if Global.SHOW_REAL_SPEED:
                        self.calc_speed_running.set()
                else:
                    raise ValueError(f"Invalid action: {next_action}")

            if not alive:
                # game over
                self.snake_move_timer.pause()
                if Global.SHOW_REAL_SPEED:
                    self.calc_speed_running.clear()
                    self.head_deque.clear()
                    self.real_speed = 0
                return Action.GAME_OVER, result

            self.clock.tick(Global.FPS)

    def play(self, direction: Direction | None = None, full_speed=False, teleport=False) -> \
            tuple[bool, GameState, bool, bool, bool]:
        """
        control snake to move and update game status

        :param direction: if not None, control snake by `direction`, else control by keyboard
        :param full_speed: set if snake move at full speed (ignore timer)
        :param teleport: set if snake can teleport when hit the border
        :return: (alive, game_state, collision_with_food, collision_with_body, collision_with_wall)
        """

        if direction is not None:
            self.snake.change_direction(direction)
        else:
            # control by keyboard
            self.control()
        if not full_speed and self.snake.speed_changed:
            self.snake_move_timer.set_interval_sec(1 / (1.5 * self.snake.move_speed))
            self.snake.speed_changed = False

        status = (True, GameState.PLAYING)
        collision = (False, False, False)

        if full_speed or self.snake_move_timer.arrived:
            self.snake.walk(self.surface, teleport=teleport)
            self.move_distance += 1

            if Global.SHOW_REAL_SPEED:
                head_pos = (self.snake.x[0], self.snake.y[0])
                cur_time = time.time()
                self.head_deque.append((head_pos, cur_time))

            collision = self.check_collision()
            if collision[0]:
                # check upgrade after eating food
                self.check_upgrade()

            self.update_hungry_level()
            status = self.check_alive()
        return status[0], status[1], collision[0], collision[1], collision[2]

    def pause(self) -> Action:
        blur_surface = pre_surface = self.surface.copy()

        resume_button = Button(
            title="Resume", color=(pygame.Color("white"), pygame.Color("green")), position=(0.5, 0.65)
        )
        restart_button = Button(
            title="Restart", color=(pygame.Color("white"), pygame.Color("cyan")), position=(0.5, 0.75)
        )
        back_to_main_menu_button = Button(
            title="Back to main menu", color=(pygame.Color("white"), pygame.Color("yellow")), position=(0.5, 0.85)
        )

        self.board.add(resume_button, restart_button, back_to_main_menu_button)

        entering = True
        releasing = False
        blur_kernel_size = 1

        while True:
            EventManager.get_event()
            self.board.update_button_status()

            if entering:
                blur_surface = Util.gaussian_blur(pre_surface, blur_kernel_size)
                if blur_kernel_size > 60:
                    entering = False
                else:
                    blur_kernel_size += 6

            if releasing:
                ''' gradually remove blur before leaving pause page '''
                blur_surface = Util.gaussian_blur(pre_surface, blur_kernel_size)
                blur_kernel_size -= 6
                if blur_kernel_size <= 1:
                    self.board.clear_button()
                    self.surface.blit(pre_surface, (0, 0))
                    return Action.CONTINUE

            self.surface.blit(blur_surface, (0, 0))

            if not releasing:
                self.board.add(
                    Text("Paused", pygame.Color("cyan"), (0.5, 0.25), name="title", font_size=5 * Global.UI_SCALE)
                )
                self.board.draw(self.surface)

            if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.pause_list) \
                    or resume_button.is_triggered:
                entering = not entering
                releasing = not releasing

            if restart_button.is_triggered:
                self.board.clear_button()
                self.reset_game()
                return Action.START_GAME

            if back_to_main_menu_button.is_triggered:
                self.board.clear_button()
                self.reset_game()
                return Action.MAIN_MENU

            Util.update_screen()
            self.clock.tick(Global.FPS)

    def init_game_surface(self) -> None:
        self.set_base_color(Global.BACK_GROUND_COLOR)
        self.wall.draw(self.surface)
        self.snake.draw(self.surface)
        self.food_manager.draw()

    def update_board(self) -> None:
        # self.wall.draw(self.surface)
        # self.snake.draw(self.surface)
        # self.food_manager.draw(self.surface)
        self.surface.fill(Global.STATUS_BAR_COLOR, (0, 0, self.surface.get_width(), Global.TOP_PADDING))
        self.surface.fill(Global.STATUS_BAR_COLOR, (0, self.surface.get_height() - Global.BOTTOM_PADDING,
                                                    self.surface.get_width(), Global.BOTTOM_PADDING))
        self.snake.health.draw(self.surface)
        self.snake.hungry.draw(self.surface)
        self.board.draw(self.surface)

    def set_base_color(self, color) -> None:
        self.surface.fill(color)

    def control(self) -> None:
        if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.left_list):
            self.snake.change_direction(Direction.LEFT)
        elif EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.right_list):
            self.snake.change_direction(Direction.RIGHT)
        elif EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.up_list):
            self.snake.change_direction(Direction.UP)
        elif EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.down_list):
            self.snake.change_direction(Direction.DOWN)

    def get_score(self) -> int:
        return self.snake.length - self.snake.init_length + self.score

    def check_collision(self) -> tuple[bool, bool, bool]:
        return (
            self.collide_with_food(),
            self.collide_with_body(),
            self.collide_with_wall()
        )

    def collide_with_food(self) -> bool:
        for food in self.food_manager.food_list:
            for i in range(food.count):
                if self.is_collision(self.snake.x[0], self.snake.y[0], food.x[i], food.y[i]):
                    food.update(self.grid, self.surface, index=i)
                    self.snake.hungry.increase_satiety(food.add_satiety)
                    self.snake.health.increase(-food.toxic_level)
                    self.snake.increase_length(food.increase_length)
                    self.snake.increase_speed(food.increase_speed)
                    self.score += food.add_score
                    self.eat_food_count += 1
                    return True
        return False

    def collide_with_body(self) -> bool:
        if (self.snake.x[0], self.snake.y[0]) in zip(self.snake.x[4:], self.snake.y[4:]):
            self.snake.health.increase(-Global.EAT_BODY_DAMAGE)
            return True
        return False

    def collide_with_wall(self) -> bool:
        if self.grid.has_wall(self.snake.x[0], self.snake.y[0]):
            self.snake.health.increase(-Global.HIT_WALL_DAMAGE)
            return True
        return False

    def update_hungry_level(self) -> None:
        if self.snake.hungry.hungry_step_count > 0 and \
                self.snake.hungry.hungry_step_count % max(50 - (self.level - 1) * 4, 20) == 0:
            if self.snake.hungry.get_satiety() > 0:
                # increase hungry value till satiety -> 0
                self.snake.hungry.increase_satiety(-1)
            else:
                # start to decrease health value
                self.snake.health.increase(-1)

    def check_upgrade(self) -> None:
        """
        Update the level up to MAX_LEVEL and increase movement speed when level-up.
        """
        if self.level >= Global.MAX_LEVEL:
            return
        if self.get_score() // 20 > self.level - 1:
            self.snake.increase_speed(1)
            self.level += 1

    def check_alive(self) -> tuple[bool, GameState]:
        """
        check if the snake is alive
        (snake will also die if there is no space)
        result: int: PLAYING -> snake alive; FAILED -> snake died; WINNING -> no space(win the game)
        :return: tuple(snake_alive: bool, result: int)
        """
        winning = self.grid.get_empty_count() <= 0
        failed = self.snake.health.value <= 0
        alive = not (winning or failed)
        result = GameState.PLAYING
        if failed:
            result = GameState.FAILED
        if winning:
            result = GameState.WINNING
        return alive, result

    def calc_real_speed(self) -> None:
        """
        thread: calculate the real-time speed of the snake, unit: block per second
        """
        while True:
            if len(self.head_deque) < self.head_deque.maxlen:    # pyright: ignore[reportOperatorIssue]
                time.sleep(0.1)
                continue
            total_distance = 0
            for i in range(0, len(self.head_deque) - 1):
                distance = abs(self.head_deque[i + 1][0][0] - self.head_deque[i][0][0]) + \
                           abs(self.head_deque[i + 1][0][1] - self.head_deque[i][0][1])
                total_distance += distance
            total_time = self.head_deque[-1][1] - self.head_deque[0][1]
            speed = total_distance / total_time
            self.real_speed = round(speed, 1)
            time.sleep(0.1)
            self.calc_speed_running.wait()

    def game_over(self, result: GameState = GameState.FAILED) -> Action:
        """
        the game-over menu
        :param result: GameState (default: GameState.FAILED)
        :return: Action: next_action
        """
        blur_surface = pre_surface = self.surface.copy()
        final_score = self.get_score()
        user_name = getpass.getuser()
        # print(f"Your score: {self.get_score()}")
        file_name = "high_score.json"
        data = Util.load_data_from_json_file(file_name)
        break_record = False
        best_score = final_score

        if user_name in data.keys():
            if data[user_name] < final_score:
                ''' break record '''
                # print("Congratulations, you broke your best record!")
                break_record = True
                data[user_name] = final_score
            else:
                best_score = data[user_name]
        else:
            ''' add user name to high score '''
            data[user_name] = final_score
            break_record = True

        if break_record:
            Util.write_data_to_json_file(file_name, data)

        restart_button = Button(
            title="Restart", color=(pygame.Color("white"), pygame.Color("cyan")), position=(0.5, 0.65)
        )
        back_to_main_menu_button = Button(
            title="Back to main menu", color=(pygame.Color("white"), pygame.Color("yellow")), position=(0.5, 0.8)
        )

        self.board.add(restart_button, back_to_main_menu_button)

        entering = True
        blur_kernel_size = 1

        while True:
            EventManager.get_event()
            self.board.update_button_status()

            if entering:
                blur_surface = Util.gaussian_blur(pre_surface, blur_kernel_size)
                if blur_kernel_size > 60:
                    entering = False
                else:
                    blur_kernel_size += 6

            self.surface.blit(blur_surface, (0, 0))

            if result == GameState.FAILED:
                self.board.add(
                    Text("Game over", pygame.Color("firebrick1"), (0.5, 0.25), name="title",
                         font_size=5 * Global.UI_SCALE)
                )
            elif result == GameState.WINNING:
                self.board.add(
                    Text("You win !!!", pygame.Color("springgreen3"), (0.5, 0.25), name="title",
                         font_size=5 * Global.UI_SCALE)
                )
            else:
                raise ValueError(f"Invalid {result = }")

            if break_record:
                self.board.add(
                    Text(f"New Best Score: {final_score}", pygame.Color("darkorange"), (0.5, 0.45),
                         bold=True, name="sub_title_1", font_size=2 * Global.UI_SCALE),
                    Text(f"Length: {self.snake.length}", pygame.Color("goldenrod"), (0.5, 0.55), name="sub_title_2",
                         font_size=int(1.5 * Global.UI_SCALE))
                )
            else:
                self.board.add(
                    Text(f"Best record: {best_score}", pygame.Color("white"), (0.5, 0.1), name="sub_title_1", alpha=200,
                         font_size=int(1.5 * Global.UI_SCALE)),
                    Text(f"Score: {final_score}  Length: {self.snake.length}", pygame.Color("goldenrod"), (0.5, 0.45),
                         name="sub_title_2", font_size=int(2.5 * Global.UI_SCALE))
                )

            self.board.draw(self.surface)

            if restart_button.is_triggered:
                self.board.clear_button()
                self.reset_game()
                return Action.START_GAME

            if back_to_main_menu_button.is_triggered:
                self.board.clear_button()
                self.reset_game()
                return Action.MAIN_MENU

            Util.update_screen()
            self.clock.tick(Global.FPS)

    def draw_banner(self) -> None:
        x = (self.surface.get_width() - self.banner_img.get_width()) / 2
        y = (0.5 * self.surface.get_height() - self.banner_img.get_height()) / 2
        self.surface.blit(self.banner_img, (x, y))

    @staticmethod
    def print_high_score(data) -> None:
        print("---HIGH-SCORE---")
        for key, value in data.items():
            print(f"{key}:\t{value}")
        print("----------------")

    @staticmethod
    def is_collision(x1, y1, x2, y2) -> bool:
        return x1 == x2 and y1 == y2
