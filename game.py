import getpass
from typing import NoReturn

import pygame

from animation import AnimationManager
from board import Board, Button, Text
from event import EventManager
from food import FoodManager
from settings import Global, KeyBoard
from snake import Snake
from util import Util
from wall import Wall


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("PySnake")
        pygame.display.set_icon(pygame.image.load("resources/img/icon.png"))
        self.surface = pygame.display.set_mode(Global.SCREEN_SIZE, pygame.RESIZABLE)
        self.banner_img = pygame.image.load("resources/img/banner.png").convert_alpha()
        self.banner_img = pygame.transform.rotozoom(self.banner_img, 0, Global.BLOCK_SIZE * 0.08)
        self.clock = pygame.time.Clock()

        self.animation_manager = AnimationManager()
        self.snake = Snake()
        self.wall = Wall()
        self.food_manager = FoodManager()
        self.board = Board()

        self.snake_move_timer = Util.timer()

        self.level: int = 1
        self.score: int = 0

    def main_menu(self) -> NoReturn:
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
                self.start_game()

            if exit_button.is_triggered:
                Util.quit_game()

            Util.update_screen()
            self.clock.tick(Global.FPS)

    def start_game(self) -> NoReturn:
        self.reset_game()

        while True:
            EventManager.get_event()

            self.set_base_color(Global.BACK_GROUND_COLOR)
            self.play()
            self.board.add(
                Text(f"FPS: {round(self.clock.get_fps())}", pygame.Color("white"), "left_top", alpha=255),
                Text(f"score: {self.get_score()}", pygame.Color("springgreen"), "right_top", alpha=255),
                Text(f"speed: {self.snake.move_speed}", pygame.Color("white"), "middle_top", alpha=255),
                Text(f"level: {self.level}", pygame.Color("chartreuse"), "middle_bottom", alpha=255)
            )
            self.update_surface()
            Util.update_screen()

            if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.pause_list) or \
                    EventManager.check_key_or_button(pygame.MOUSEBUTTONDOWN, 3):
                self.snake_move_timer.stop()
                self.pause()
                self.snake_move_timer.start()

            if self.snake.health.value <= 0:
                self.snake_move_timer.stop()
                self.game_over()

            self.clock.tick(Global.FPS)

    def play(self) -> None:
        self.check_direction_change()

        if self.snake.speed_changed:
            self.snake_move_timer.set_interval(1 / (1.5 * self.snake.move_speed))
            self.snake.speed_changed = False
        if self.snake_move_timer.arrived():
            self.snake.walk()
            collision = self.check_collision()
            if collision[0]:
                # check upgrade after eating food
                self.check_upgrade()
            self.check_hungry_level()

    def pause(self) -> None:
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
                    break

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
                self.start_game()

            if back_to_main_menu_button.is_triggered:
                self.board.clear_button()
                self.main_menu()

            Util.update_screen()
            self.clock.tick(Global.FPS)

    def update_surface(self) -> None:
        self.wall.draw(self.surface)
        self.snake.draw(self.surface)
        self.food_manager.draw(self.surface)
        self.snake.health.draw(self.surface)
        self.snake.hungry.draw(self.surface)
        self.board.draw(self.surface)

    def set_base_color(self, color) -> None:
        self.surface.fill(color)

    def check_direction_change(self) -> None:
        if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.left_list):
            self.snake.change_direction("left")
        elif EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.right_list):
            self.snake.change_direction("right")
        elif EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.up_list):
            self.snake.change_direction("up")
        elif EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.down_list):
            self.snake.change_direction("down")

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
            if food.count > 0:
                for i in range(food.count):
                    if self.is_collision(self.snake.x[0], self.snake.y[0], food.x[i], food.y[i]):
                        food.update(self, index=i)
                        self.snake.hungry.increase_satiety(food.add_satiety)
                        self.snake.health.increase(-food.toxic_level)
                        self.snake.increase_length(food.increase_length)
                        self.snake.increase_speed(food.increase_speed)
                        self.score += food.add_score
                        return True
        return False

    def collide_with_body(self) -> bool:
        for i in range(1, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.snake.health.increase(-1)
                return True
        return False

    def collide_with_wall(self) -> bool:
        if (self.snake.x[0], self.snake.y[0]) in self.wall.coords:
            self.snake.health.increase(-2)
            return True
        else:
            return False

    def check_hungry_level(self) -> None:
        count_when_increase = max(50 - (self.level - 1) * 4, 20)
        if self.snake.hungry.hungry_step_count >= count_when_increase:
            if self.snake.hungry.get_satiety() > 0:
                # increase hungry value till satiety -> 0
                self.snake.hungry.increase_satiety(-1)
            else:
                # start to decrease health value
                self.snake.health.increase(-1)
            # reset hungry step count
            self.snake.hungry.hungry_step_count = 0

    def check_upgrade(self) -> None:
        if self.level >= Global.MAX_LEVEL:
            return

        if self.get_score() // 20 > self.level - 1:
            self.upgrade()

    def upgrade(self) -> None:
        """
        Update level up to MAX_LEVEL and add move speed when level up.
        """
        if self.level >= Global.MAX_LEVEL:
            return
        self.snake.increase_speed(1)
        self.level += 1

    def game_over(self) -> NoReturn:
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

            self.board.add(
                Text("Game over", pygame.Color("firebrick1"), (0.5, 0.25), name="title", font_size=5 * Global.UI_SCALE)
            )
            if break_record:
                self.board.add(
                    Text(f"New Best Score: {final_score}", pygame.Color("darkorange"), (0.5, 0.45),
                         bold=True, name="sub_title_1", font_size=2 * Global.UI_SCALE)
                )
            else:
                self.board.add(
                    Text(f"Best record: {best_score}", pygame.Color("white"), (0.5, 0.1), name="sub_title_1", alpha=200,
                         font_size=int(1.5 * Global.UI_SCALE)),
                    Text(f"Score: {final_score}", pygame.Color("goldenrod"), (0.5, 0.45), name="sub_title_2",
                         font_size=int(2.5 * Global.UI_SCALE))
                )

            self.board.draw(self.surface)

            if restart_button.is_triggered:
                self.board.clear_button()
                self.start_game()

            if back_to_main_menu_button.is_triggered:
                self.board.clear_button()
                self.main_menu()

            Util.update_screen()
            self.clock.tick(Global.FPS)

    def update_food(self) -> None:
        for food in self.food_manager.food_list:
            food.update(self)

    def draw_banner(self) -> None:
        x = (self.surface.get_width() - self.banner_img.get_width()) / 2
        y = (0.5 * self.surface.get_height() - self.banner_img.get_height()) / 2
        self.surface.blit(self.banner_img, (x, y))

    def reset_game(self) -> None:
        self.snake.reset()
        self.wall.reset()
        self.food_manager.reset()
        self.update_food()
        self.snake.health.reset()
        self.snake.hungry.reset()
        self.level = 1
        self.score = 0

    @staticmethod
    def print_high_score(data) -> None:
        print("---HIGH-SCORE---")
        for key, value in data.items():
            print(f"{key}:\t{value}")
        print("----------------")

    @staticmethod
    def is_collision(x1, y1, x2, y2) -> bool:
        return x1 == x2 and y1 == y2
