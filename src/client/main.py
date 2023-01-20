import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
# import time

# from client.utils import gameclient

# if __name__ == "__main__":
#     (address, port) = (sys.argv[1], int(sys.argv[2]))  # The port used by the server
#     clientType = None
#     if sys.argv[3] == "open":
#         clientType = gameclient.GameClientType(gameclient.GameClientType.CREATE_ROOM)
#     if sys.argv[3] == "join":
#         clientType = gameclient.GameClientType(gameclient.GameClientType.JOIN_ROOM, sys.argv[4])


#     client = gameclient.GameClient(address, port, 15, clientType)
#     while True:
#         roomCode = client.getRoomCode()
#         if roomCode is not None:
#             print(f"Room code: {roomCode}")
#             break
#         time.sleep(0.333)

#     while True:
#         print(client.gameData())
#         time.sleep(0.333)

# Simple pygame program


# Import and initialize the pygame library

import pygame

from client.application import GameApp


pygame.init()

app = GameApp((1280, 720))
app.run()

pygame.quit()
