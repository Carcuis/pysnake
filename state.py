from typing import NoReturn

from game import Game
from util import GameState, Motion, Util


class StateManager:
    def __init__(self) -> None:
        self.current_state: GameState = GameState.PLAYING
        self.motion: Motion = Motion.MAIN_MENU
        self.game: Game = Game()

    def run(self) -> NoReturn:
        while True:
            if self.motion == Motion.MAIN_MENU:
                self.motion = self.game.main_menu()
            elif self.motion == Motion.START_GAME:
                self.motion, self.current_state = self.game.start_game()
            elif self.motion == Motion.GAME_OVER:
                self.motion = self.game.game_over(self.current_state)
            elif self.motion == Motion.QUIT_GAME:
                Util.quit_game()
