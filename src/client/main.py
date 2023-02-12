import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--addr",
        help="The IPv4 address of the game server (Default is 127.0.0.1)",
        nargs="?",
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="The port which the game server listens on (Default is 10001)",
        nargs="?",
        default="10001",
        type=int,
    )
    parser.add_argument(
        "-s",
        "--screen",
        help="The dimensions of the game window (Default is 1280x720)",
        nargs="?",
        default="1280x720",
        choices=["640x360", "960x540", "1280x720", "1920x1080"],
        type=str,
    )
    args = parser.parse_args(sys.argv[1:])

    import os

    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
    import pygame
    from client.application import GameApp

    pygame.init()

    [width, height] = args.screen.split("x")
    app = GameApp(args.addr, args.port, (int(width), int(height)))
    app.run()

    pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
