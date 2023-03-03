#!/usr/bin/env python3

from state import StateManager
from util import Util


def main():
    state_manager = StateManager()
    state_manager.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
        Util.quit_game()  # ensure timer threads terminated after interrupt
