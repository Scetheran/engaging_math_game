import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from server.utils import gameserver

(HOST, PORT) = (
    sys.argv[1],
    int(sys.argv[2]),
)  # Port to listen on (non-privileged ports are > 1023)


def main():
    server = gameserver.GameServer(HOST, PORT, 30)
    server.run()

if __name__ == "__main__":
    sys.exit(main())
