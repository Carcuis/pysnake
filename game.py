import getpass
import pygame
from pygame.locals import *
from settings import *
from util import Util
from event_manager import EventManager
from board import Board
from snake import Snake
from food import FoodManager
from health import Health, Hungry
from wall import Wall


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PySnake")
        pygame.display.set_icon(pygame.image.load("resources/imgs/icon.png"))
        self.surface = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)
        self.banner_img = pygame.image.load("resources/imgs/banner.png").convert_alpha()
        self.banner_img = pygame.transform.rotozoom(self.banner_img, 0, BLOCK_SIZE * 0.08)
        self.clock = pygame.time.Clock()

        self.event_manager = EventManager(self)
        self.snake = Snake(self.surface, self)
        self.wall = Wall(self.surface, self)
        self.food_manager = FoodManager(self.surface, self)
        self.current_text_board = Board(self.surface)
        self.health = Health(self.surface, self)
        self.hungry = Hungry(self.surface, self)

        self.level = 1
        self.tick_count = 0
        self.score = 0
        self.__score_cache = 0
        self.__blur_kernel_size = 1

    def main_menu(self):
        maintain = True

        hover_status = {"start_button": False, "exit_button": False}
        is_clicked = {"start_button": False, "exit_button": False}

        while maintain:
            self.event_manager.get_event()
            self.set_base_color(BACK_GROUND_COLOR)
            self.draw_banner()

            self.current_text_board.text.add(
                "> Start <" if hover_status["start_button"] else "Start",
                pygame.Color("green") if hover_status["start_button"] else pygame.Color("white"),
                (0.5, 0.65),
                bold=True if hover_status["start_button"] else False,
                alpha=255 if hover_status["start_button"] else 200,
                name="start_button", font_size=2*UI_SCALE)
            self.current_text_board.text.add(
                "> Exit game <" if hover_status["exit_button"] else "Exit game",
                pygame.Color("red") if hover_status["exit_button"] else pygame.Color("white"),
                (0.5, 0.85),
                bold=True if hover_status["exit_button"] else False,
                alpha=255 if hover_status["exit_button"] else 200,
                name="exit_button", font_size=2*UI_SCALE)

            self.current_text_board.draw()

            result = self.get_board_button_status(self.current_text_board)
            hover_status.update(result[0])
            is_clicked.update(result[1])

            if self.event_manager.check_key_or_button(KEYDOWN, K_RETURN) or\
                    is_clicked["start_button"]:
                self.start_game()

            if self.event_manager.check_key_or_button(KEYDOWN, K_q) or \
                    self.event_manager.check_key_or_button(KEYDOWN, K_ESCAPE) or \
                    is_clicked["exit_button"]:
                self.quit_game()

            self.current_text_board.clear()

            Util.update_screen()
            self.clock.tick(FPS)
        self.quit_game()

    def start_game(self):
        self.reset_game()

        running = True
        while running:
            self.event_manager.get_event()

            self.set_base_color(BACK_GROUND_COLOR)
            self.play()
            self.in_game_draw_surface()
            Util.update_screen()
            self.parse_event()
            self.check_health()

            self.clock.tick(FPS)
            self.tick_count += 1

        self.main_menu()

    def play(self):
        self.snake.walk()

        # execute only after actually walk
        if not self.snake.move_lock:
            self.check_collision()
            self.check_score()
            self.check_hungry_level()

        self.update_status_board()

    def pause(self):
        blur_surface = pre_surface = self.surface.copy()
        pause_board = Board(self.surface)

        hover_status = {"resume_button": False, "back_to_main_menu_button": False}
        is_clicked = {"resume_button": False, "back_to_main_menu_button": False}

        maintain = True
        release = False
        while maintain:
            self.event_manager.get_event()

            if not release:
                if self.__blur_kernel_size < 59:
                    blur_surface = Util.gaussian_blur(pre_surface, self.__blur_kernel_size)
                    self.__blur_kernel_size += 6
            else:
                ''' gradually remove blur before leaving pause page '''
                blur_surface = Util.gaussian_blur(pre_surface, self.__blur_kernel_size)
                self.__blur_kernel_size -= 6
                if self.__blur_kernel_size <= 1:
                    self.__blur_kernel_size = 1
                    maintain = False

            self.surface.blit(blur_surface, (0, 0))

            if not release:
                pause_board.text.add("Paused", pygame.Color("cyan"), (0.5, 0.25), name="title", font_size=5 * UI_SCALE)
                pause_board.text.add(
                    "> Resume <" if hover_status["resume_button"] else "Resume",
                    pygame.Color("green") if hover_status["resume_button"] else pygame.Color("white"),
                    (0.5, 0.65),
                    bold=True if hover_status["resume_button"] else False,
                    alpha=255 if hover_status["resume_button"] else 200,
                    name="resume_button", font_size=2 * UI_SCALE)
                pause_board.text.add(
                    "> Back to main menu <" if hover_status["back_to_main_menu_button"] else "Back to main menu",
                    pygame.Color("yellow") if hover_status["back_to_main_menu_button"] else pygame.Color("white"),
                    (0.5, 0.75),
                    bold=True if hover_status["back_to_main_menu_button"] else False,
                    alpha=255 if hover_status["back_to_main_menu_button"] else 200,
                    name="back_to_main_menu_button", font_size=2 * UI_SCALE)

                pause_board.draw()

                result = self.get_board_button_status(pause_board)
                hover_status.update(result[0])
                is_clicked.update(result[1])

            if self.event_manager.check_key_or_button(KEYDOWN, K_p) or \
                    self.event_manager.check_key_or_button(KEYDOWN, K_ESCAPE) or \
                    self.event_manager.check_key_or_button(KEYDOWN, K_SPACE) or \
                    is_clicked["resume_button"]:
                release = True

            if is_clicked["back_to_main_menu_button"]:
                self.__blur_kernel_size = 1
                self.main_menu()

            pause_board.clear()
            Util.update_screen()
            self.clock.tick(FPS)

    def in_game_draw_surface(self):
        self.wall.draw()
        self.snake.draw()
        self.food_manager.draw()
        self.health.draw()
        self.hungry.draw()
        self.current_text_board.draw()
        self.current_text_board.clear()

    def set_base_color(self, color):
        self.surface.fill(color)

    def parse_event(self):
        if self.event_manager.check_key_or_button(KEYDOWN, K_LEFT) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_h) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_KP4):
            self.snake.change_direction("left")
        elif self.event_manager.check_key_or_button(KEYDOWN, K_RIGHT) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_l) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_KP6):
            self.snake.change_direction("right")
        elif self.event_manager.check_key_or_button(KEYDOWN, K_UP) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_k) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_KP8):
            self.snake.change_direction("up")
        elif self.event_manager.check_key_or_button(KEYDOWN, K_DOWN) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_j) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_KP5):
            self.snake.change_direction("down")
        elif self.event_manager.check_key_or_button(KEYDOWN, K_p) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_ESCAPE) or \
                self.event_manager.check_key_or_button(KEYDOWN, K_SPACE) or \
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
        bite_body = False
        for i in range(1, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                bite_body = True
                break
        if bite_body:
            self.health.increase_health(-1)

    def check_collision_with_wall(self):
        hit_wall = False
        if (self.snake.x[0], self.snake.y[0]) in self.wall.coords:
            hit_wall = True
        if hit_wall:
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
        if self.__score_cache == self.get_score():
            # upgrade only on self.score updates
            return
        self.__score_cache = self.get_score()
        if self.__score_cache // 20 > self.level - 1:
            self.upgrade()

    def upgrade(self):
        """
        Update level up to 8 and add move speed if level up.
        """
        if self.level > 7:
            return
        self.snake.move_speed += 1
        self.level += 1

    def game_over(self):
        blur_surface = pre_surface = self.surface.copy()
        game_over_board = Board(self.surface)
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

        hover_status = {"restart_button": False, "back_to_main_menu_button": False}
        is_clicked = {"restart_button": False, "back_to_main_menu_button": False}

        maintain = True

        while maintain:
            self.event_manager.get_event()

            if self.__blur_kernel_size < 59:
                blur_surface = Util.gaussian_blur(pre_surface, self.__blur_kernel_size)
                self.__blur_kernel_size += 6

            self.surface.blit(blur_surface, (0, 0))

            game_over_board.text.add("Game over", pygame.Color("firebrick1"),
                                     (0.5, 0.25), name="title", font_size=5*UI_SCALE)
            if break_record:
                game_over_board.text.add(f"New Best Score: {final_score}", pygame.Color("darkorange"),
                                         (0.5, 0.45), bold=True, name="sub_title_1", font_size=2*UI_SCALE)
            else:
                game_over_board.text.add(f"Best record: {best_score}", pygame.Color("white"),
                                         (0.5, 0.1), name="sub_title_1", alpha=200, font_size=int(1.5*UI_SCALE))
                game_over_board.text.add(f"Score: {final_score}", pygame.Color("goldenrod"),
                                         (0.5, 0.45), name="sub_title_2", font_size=int(2.5*UI_SCALE))
            game_over_board.text.add(
                "> Restart <" if hover_status["restart_button"] else "Restart",
                pygame.Color("green") if hover_status["restart_button"] else pygame.Color("white"),
                (0.5, 0.65),
                bold=True if hover_status["restart_button"] else False,
                alpha=255 if hover_status["restart_button"] else 200,
                name="restart_button", font_size=2*UI_SCALE)
            game_over_board.text.add(
                "> Back to main menu <" if hover_status["back_to_main_menu_button"] else "Back to main menu",
                pygame.Color("yellow") if hover_status["back_to_main_menu_button"] else pygame.Color("white"),
                (0.5, 0.75),
                bold=True if hover_status["back_to_main_menu_button"] else False,
                alpha=255 if hover_status["back_to_main_menu_button"] else 200,
                name="back_to_main_menu_button", font_size=2*UI_SCALE)

            game_over_board.draw()

            result = self.get_board_button_status(game_over_board)
            hover_status.update(result[0])
            is_clicked.update(result[1])

            if is_clicked["restart_button"]:
                self.start_game()

            if is_clicked["back_to_main_menu_button"]:
                self.__blur_kernel_size = 1
                self.main_menu()

            game_over_board.clear()
            Util.update_screen()
            self.clock.tick(FPS)

        self.__blur_kernel_size = 1

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

    def get_board_button_status(self, _board):
        hover_status = dict()
        is_clicked = dict()

        for i in range(len(_board.text.text_array)):
            rect = _board.text.text_surface_array[i].get_rect()
            rect.topleft = _board.text.text_array[i]["left_top"]
            if rect.collidepoint(self.event_manager.mouse_pos):
                hover_status[_board.text.text_array[i]["name"]] = True
                if self.event_manager.check_key_or_button(MOUSEBUTTONUP, 1):
                    is_clicked[_board.text.text_array[i]["name"]] = True
                else:
                    is_clicked[_board.text.text_array[i]["name"]] = False
            else:
                hover_status[_board.text.text_array[i]["name"]] = False
                is_clicked[_board.text.text_array[i]["name"]] = False

        return hover_status, is_clicked

    def reset_game(self):
        self.snake.reset()
        self.wall.reset()
        self.food_manager.reset()
        self.update_food()
        self.health.reset()
        self.hungry.reset()
        self.level = 1
        self.tick_count = 0
        self.score = 0
        self.__score_cache = 0
        self.__blur_kernel_size = 1

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
