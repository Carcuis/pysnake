import getpass
import pygame
from pygame.locals import *
from settings import Global, KeyBoard
from util import Util
from event_manager import EventManager
from board import Board, Button, ButtonManager
from snake import Snake
from food import FoodManager
from health import Health, Hungry
from wall import Wall


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PySnake")
        pygame.display.set_icon(pygame.image.load("resources/img/icon.png"))
        self.surface = pygame.display.set_mode(Global.SCREEN_SIZE, RESIZABLE)
        self.banner_img = pygame.image.load("resources/img/banner.png").convert_alpha()
        self.banner_img = pygame.transform.rotozoom(self.banner_img, 0, Global.BLOCK_SIZE * 0.08)
        self.clock = pygame.time.Clock()

        self.event_manager = EventManager(self)
        self.snake = Snake(self.surface, self)
        self.wall = Wall(self.surface, self)
        self.food_manager = FoodManager(self.surface, self)
        self.current_text_board = Board(self.surface)
        self.health = Health(self.surface, self)
        self.hungry = Hungry(self.surface, self)

        self.event_timer_snake_move = pygame.USEREVENT

        self.level: int = 1
        self.score: int = 0
        self._score_cache: int = 0
        self._blur_kernel_size: int = 1

    def main_menu(self):
        maintain = True

        start_button = Button(
            title="Start", color=(pygame.Color("white"), pygame.Color("green")), position=(0.5, 0.65)
        )
        exit_button = Button(
            title="Exit game", color=(pygame.Color("white"), pygame.Color("red")), position=(0.5, 0.85)
        )

        button_manager = ButtonManager(start_button, exit_button)

        while maintain:
            self.event_manager.get_event()
            button_manager.update_status(self.event_manager)

            self.set_base_color(Global.BACK_GROUND_COLOR)
            self.draw_banner()

            button_manager.add_text_to_board(self.current_text_board)

            self.current_text_board.draw()

            if start_button.is_triggered:
                self.start_game()

            if exit_button.is_triggered:
                self.quit_game()

            Util.update_screen()
            self.clock.tick(Global.FPS)
        self.quit_game()

    def start_game(self):
        self.reset_game()

        running = True
        while running:
            self.event_manager.get_event()

            self.set_base_color(Global.BACK_GROUND_COLOR)
            self.play()
            self.in_game_draw_surface()
            Util.update_screen()
            self.parse_event()
            self.check_health()

            self.clock.tick(Global.FPS)

        self.main_menu()

    def play(self):
        if self.snake.move_speed != self.snake.move_speed_buffer:
            pygame.time.set_timer(self.event_timer_snake_move, int(1000 / (1.5 * self.snake.move_speed)))
            self.snake.move_speed_buffer = self.snake.move_speed
        if self.event_manager.match_event_type(self.event_timer_snake_move):
            self.snake.walk()
            self.snake.move_lock = False
        else:
            self.snake.move_lock = True

        # execute only after actually walk
        if not self.snake.move_lock:
            self.check_collision()
            self.check_score()
            self.check_hungry_level()

        self.update_status_board()

    def pause(self):
        blur_surface = pre_surface = self.surface.copy()
        self.current_text_board = Board(self.surface)

        resume_button = Button(
            title="Resume", color=(pygame.Color("white"), pygame.Color("green")), position=(0.5, 0.65)
        )
        restart_button = Button(
            title="Restart", color=(pygame.Color("white"), pygame.Color("cyan")), position=(0.5, 0.75)
        )
        back_to_main_menu_button = Button(
            title="Back to main menu", color=(pygame.Color("white"), pygame.Color("yellow")), position=(0.5, 0.85)
        )

        button_manager = ButtonManager(resume_button, restart_button, back_to_main_menu_button)

        maintain = True
        release = False
        while maintain:
            self.event_manager.get_event()
            button_manager.update_status(self.event_manager)

            if not release:
                if self._blur_kernel_size < 59:
                    blur_surface = Util.gaussian_blur(pre_surface, self._blur_kernel_size)
                    self._blur_kernel_size += 6
            else:
                ''' gradually remove blur before leaving pause page '''
                blur_surface = Util.gaussian_blur(pre_surface, self._blur_kernel_size)
                self._blur_kernel_size -= 6
                if self._blur_kernel_size <= 1:
                    self._blur_kernel_size = 1
                    maintain = False

            self.surface.blit(blur_surface, (0, 0))

            if not release:
                self.current_text_board.text.add(
                    "Paused", pygame.Color("cyan"), (0.5, 0.25), name="title", font_size=5 * Global.UI_SCALE
                )
                button_manager.add_text_to_board(self.current_text_board)

                self.current_text_board.draw()

            if self.event_manager.check_key_or_button(KEYDOWN, KeyBoard.pause_list) or resume_button.is_triggered:
                release = True

            if restart_button.is_triggered:
                self.start_game()

            if back_to_main_menu_button.is_triggered:
                self._blur_kernel_size = 1
                self.main_menu()

            Util.update_screen()
            self.clock.tick(Global.FPS)

    def in_game_draw_surface(self):
        self.wall.draw()
        self.snake.draw()
        self.food_manager.draw()
        self.health.draw()
        self.hungry.draw()
        self.current_text_board.draw()

    def set_base_color(self, color):
        self.surface.fill(color)

    def parse_event(self):
        if self.event_manager.check_key_or_button(KEYDOWN, KeyBoard.left_list):
            self.snake.change_direction("left")
        elif self.event_manager.check_key_or_button(KEYDOWN, KeyBoard.right_list):
            self.snake.change_direction("right")
        elif self.event_manager.check_key_or_button(KEYDOWN, KeyBoard.up_list):
            self.snake.change_direction("up")
        elif self.event_manager.check_key_or_button(KEYDOWN, KeyBoard.down_list):
            self.snake.change_direction("down")
        elif self.event_manager.check_key_or_button(KEYDOWN, KeyBoard.pause_list) or \
                self.event_manager.check_key_or_button(MOUSEBUTTONDOWN, 3):
            self.pause()

    def get_score(self):
        return self.snake.length - self.snake.init_length + self.score

    def check_collision(self):
        self.check_collision_with_food()
        self.check_collision_with_body()
        self.check_collision_with_wall()

    def check_collision_with_food(self):
        collision = False
        for food in self.food_manager.food_list:
            if food.count > 0:
                for i in range(food.count):
                    if self.is_collision(self.snake.x[0], self.snake.y[0], food.x[i], food.y[i]):
                        collision = True
                        food.update(i)
                        self.hungry.increase_satiety(food.add_satiety)
                        self.health.increase_health(-food.toxic_level)
                        self.snake.increase_length(food.increase_length)
                        self.snake.increase_speed(food.increase_speed)
                        self.score += food.add_score
                        break
            if collision:
                break

    def check_collision_with_body(self):
        for i in range(1, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.health.increase_health(-1)
                break

    def check_collision_with_wall(self):
        if (self.snake.x[0], self.snake.y[0]) in self.wall.coords:
            self.health.increase_health(-2)

    def check_health(self):
        if self.health.value <= 0:
            self.game_over()

    def check_hungry_level(self):
        count_when_increase = max(50 - (self.level - 1) * 4, 20)
        if self.hungry.hungry_step_count >= count_when_increase:
            if self.hungry.get_satiety() > 0:
                # increase hungry value till satiety -> 0
                self.hungry.increase_satiety(-1)
            else:
                # start to decrease health value
                self.health.increase_health(-1)
            # reset hungry step count
            self.hungry.hungry_step_count = 0

    def check_score(self):
        if self._score_cache == self.get_score():
            # upgrade only on self.score updates
            return
        if self.level >= Global.MAX_LEVEL:
            return

        self._score_cache = self.get_score()
        if self._score_cache // 20 > self.level - 1:
            self.upgrade()

    def upgrade(self):
        """
        Update level up to 8 and add move speed if level up.
        """
        if self.level > 7:
            return
        self.snake.increase_speed(1)
        self.level += 1

    def game_over(self):
        blur_surface = pre_surface = self.surface.copy()
        self.current_text_board = Board(self.surface)
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
            title="Back to main menu", color=(pygame.Color("white"), pygame.Color("yellow")), position=(0.5, 0.75)
        )

        button_manager = ButtonManager(restart_button, back_to_main_menu_button)

        maintain = True

        while maintain:
            self.event_manager.get_event()
            button_manager.update_status(self.event_manager)

            if self._blur_kernel_size < 59:
                blur_surface = Util.gaussian_blur(pre_surface, self._blur_kernel_size)
                self._blur_kernel_size += 6

            self.surface.blit(blur_surface, (0, 0))

            self.current_text_board.text.add("Game over", pygame.Color("firebrick1"),
                                             (0.5, 0.25), name="title", font_size=5 * Global.UI_SCALE)
            if break_record:
                self.current_text_board.text.add(f"New Best Score: {final_score}", pygame.Color("darkorange"),
                                                 (0.5, 0.45), bold=True, name="sub_title_1",
                                                 font_size=2 * Global.UI_SCALE)
            else:
                self.current_text_board.text.add(f"Best record: {best_score}", pygame.Color("white"),
                                                 (0.5, 0.1), name="sub_title_1", alpha=200,
                                                 font_size=int(1.5 * Global.UI_SCALE))
                self.current_text_board.text.add(f"Score: {final_score}", pygame.Color("goldenrod"),
                                                 (0.5, 0.45), name="sub_title_2", font_size=int(2.5 * Global.UI_SCALE))

            button_manager.add_text_to_board(self.current_text_board)

            self.current_text_board.draw()

            if restart_button.is_triggered:
                self.start_game()

            if back_to_main_menu_button.is_triggered:
                self._blur_kernel_size = 1
                self.main_menu()

            Util.update_screen()
            self.clock.tick(Global.FPS)

        self._blur_kernel_size = 1

        self.quit_game()

    def update_food(self):
        # update in Game after FoodManager.__init__() to avoid
        # `AttributeError: 'Game' object has no attribute 'food_manager'`
        for food in self.food_manager.food_list:
            food.update()

    def draw_banner(self):
        x = (self.surface.get_width() - self.banner_img.get_width()) / 2
        y = (0.5 * self.surface.get_height() - self.banner_img.get_height()) / 2
        self.surface.blit(self.banner_img, (x, y))

    def update_status_board(self):
        self.current_text_board.text.add(f"FPS: {round(self.clock.get_fps())}",
                                         pygame.Color("white"), "left_top", alpha=255)
        self.current_text_board.text.add(f"score: {self.get_score()}",
                                         pygame.Color("springgreen"), "right_top", alpha=255)
        self.current_text_board.text.add(f"speed: {self.snake.move_speed}",
                                         pygame.Color("white"), "middle_top", alpha=255)
        self.current_text_board.text.add(f"level: {self.level}",
                                         pygame.Color("chartreuse"), "middle_bottom", alpha=255)

    def reset_game(self):
        self.snake.reset()
        self.wall.reset()
        self.food_manager.reset()
        self.update_food()
        self.health.reset()
        self.hungry.reset()
        self.level = 1
        self.score = 0
        self._score_cache = 0
        self._blur_kernel_size = 1

    @staticmethod
    def print_high_score(data):
        print("---HIGH-SCORE---")
        for key, value in data.items():
            print(f"{key}:\t{value}")
        print("----------------")

    @staticmethod
    def is_collision(x1, y1, x2, y2):
        return x1 == x2 and y1 == y2

    @staticmethod
    def quit_game():
        print("\033[1;36mBye.\033[0m")
        exit()
