import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from server.gameserver import gameserver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--addr",
        help="The IPv4 address to bind to (Default is 127.0.0.1)",
        nargs="?",
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="The port to listen on (Default is 10001)",
        nargs="?",
        default="10001",
        type=int,
    )
    parser.add_argument(
        "-t",
        "--tickrate",
        help="The ticks per second at which the separate game processes will run (Default is 30)",
        nargs="?",
        default="30",
        type=int,
    )
    parser.add_argument(
        "-r",
        "--rooms",
        help="The maximum amount of game processes that can be spawned (Default is 100)",
        nargs="?",
        default="100",
        type=int,
    )
    args = parser.parse_args(sys.argv[1:])
    server = gameserver.GameServer(args.addr, args.port, args.tickrate, args.rooms)
    server.run()


if __name__ == "__main__":
    sys.exit(main())
