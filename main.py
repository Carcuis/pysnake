from game import Game


def main():
    game = Game()
    game.main_menu()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
