#!/usr/bin/env python3

from game import Game
from util import Util


def main():
    game = Game()
    game.main_menu()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
        Util.quit_game()  # ensure timer threads terminated after interrupt
