from typing import NoReturn

from game import Game
from util import Action, GameState, Util


class StateManager:
    def __init__(self) -> None:
        self.current_state: GameState = GameState.PLAYING
        self.action: Action = Action.MAIN_MENU
        self.game: Game = Game()

    def run(self) -> NoReturn:
        while True:
            if self.action == Action.MAIN_MENU:
                self.action = self.game.main_menu()
            elif self.action == Action.START_GAME:
                self.action, self.current_state = self.game.start_game()
            elif self.action == Action.GAME_OVER:
                self.action = self.game.game_over(self.current_state)
            elif self.action == Action.QUIT_GAME:
                Util.quit_game()
