import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

import pygame

from client.application import GameApp


pygame.init()

app = GameApp((1280, 720))
app.run()

pygame.quit()
