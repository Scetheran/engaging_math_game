import time

import pygame
from client.common.layer import GameAppLayer


class GUILayer(GameAppLayer):
    _LAST_MOVEMENT_CAUSE_KEYBOARD = 0
    _LAST_MOVEMENT_CAUSE_MOUSE = 1

    def __init__(self, name):
        super().__init__(name)
        self._lastMovementCause = GUILayer._LAST_MOVEMENT_CAUSE_MOUSE
        self._internalMouseMoveOccurred = False
        self._lastMouseMovementTime = time.time()

    def lastMovementCause(self):
        return self._lastMovementCause

    def hideMouseAtPos(self, pos):
        if not pygame.mouse.get_visible():
            pygame.mouse.set_pos(pos)
            self._internalMouseMoveOccurred = True

    # Add more _handle*****Event if necessary
    def _handleKeyPressedEvent(self, event):
        return False

    def _handleMouseMovedEvent(self, event):
        return False

    def _handleMouseLBClickedEvent(self, event):
        return False

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            self._lastMovementCause = GUILayer._LAST_MOVEMENT_CAUSE_KEYBOARD
            return self._handleKeyPressedEvent(event)
        elif event.type == pygame.MOUSEMOTION:
            if not self._internalMouseMoveOccurred:
                self._lastMovementCause = GUILayer._LAST_MOVEMENT_CAUSE_MOUSE
                self._lastMouseMovementTime = time.time()
                if not pygame.mouse.get_visible():
                    pygame.mouse.set_visible(True)
            else:
                self._internalMouseMoveOccurred = False
            return self._handleMouseMovedEvent(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                return self._handleMouseLBClickedEvent(event)

    def _onRender(self, screen):
        pass

    def onRender(self, screen):
        self._onRender(screen)

        if (
            pygame.mouse.get_visible()
            and self._lastMouseMovementTime + 0.5 < time.time()
        ):
            pygame.mouse.set_visible(False)
