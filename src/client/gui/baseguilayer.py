import time

import pygame
from client.common.layer import GameAppLayer
from client.common.dataobj import DataObject


class GUILayer(GameAppLayer):
    _LAST_MOVEMENT_CAUSE_KEYBOARD = 0
    _LAST_MOVEMENT_CAUSE_MOUSE = 1

    def __init__(self, name):
        super().__init__(name)
        self._lastMovementCause = GUILayer._LAST_MOVEMENT_CAUSE_MOUSE
        self._internalMouseMoveOccurred = False
        self._lastMouseMovementTime = time.time()

        self._isAwaitingSwitchOff = False
        self._switchOffCountdownStart = None
        self._switchOffDelay = None
        self._goodbyeEvents = None

    def _generateGameConfig(self):
        SCREEN_SIZE = pygame.display.get_window_size()
        SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_SIZE
        SCREEN_CENTER_X = SCREEN_WIDTH // 2
        SCREEN_CENTER_Y = SCREEN_HEIGHT // 2
        SCREEN_CENTER = SCREEN_CENTER_X, SCREEN_CENTER_Y
        TILE_SIZE = SCREEN_WIDTH // 16
        TILE_BORDER_WIDTH = TILE_SIZE // 16
        TILE_SELECTED_BORDER_WIDTH = TILE_SIZE // 40
        TILE_BORDER_RADIUS = TILE_SIZE // 20
        TILE_SPACING = TILE_SIZE // 40
        TILE_FONT_SIZE = TILE_SIZE // 2
        TILE_FONT = pygame.font.SysFont("Arial", TILE_FONT_SIZE, bold=True)
        TILE_SELECTOR_OFFSET = TILE_SIZE // 20
        TILE_SELECTOR_OFFSET_BORDER_WIDTH = TILE_SIZE // 20
        TILE_SELECTOR_RECT_BORDER_COLOR = (200, 200, 200)
        TILE_RECT_BORDER_COLOR = (40, 40, 40)
        TILE_AVAILABLE_COLOR = (45, 140, 60)
        TILE_UNAVAILABLE_COLOR = (250, 40, 60)
        BACKGROUND_COLOR = (140, 40, 60)
        SCOREBOARD_SIZE2 = (2 * TILE_SIZE, TILE_SIZE)
        OWN_SCOREBOARD_POS = (TILE_SIZE, SCREEN_CENTER_Y + 3 * TILE_SIZE)
        ENEMY_SCOREBOARD_POS = (
            SCREEN_WIDTH - 3 * TILE_SIZE,
            SCREEN_CENTER_Y - 4 * TILE_SIZE,
        )
        SCORE_FONT = pygame.font.SysFont("Arial", TILE_FONT_SIZE // 2, bold=True)
        MENU_ITEM_SELECTOR_OFFSET = TILE_SIZE // 15
        return DataObject(
            screenWidth=SCREEN_WIDTH,
            screenHeight=SCREEN_HEIGHT,
            screenSize=SCREEN_SIZE,
            screenCenterX=SCREEN_CENTER_X,
            screenCenterY=SCREEN_CENTER_Y,
            screenCenter=SCREEN_CENTER,
            tileSize=TILE_SIZE,
            tileBorderWidth=TILE_BORDER_WIDTH,
            tileSelectedBorderWidth=TILE_SELECTED_BORDER_WIDTH,
            tileBorderRadius=TILE_BORDER_RADIUS,
            tileSpacing=TILE_SPACING,
            tileFontSize=TILE_FONT_SIZE,
            tileSelectorOffset=TILE_SELECTOR_OFFSET,
            tileSelectorOffsetBorderWidth=TILE_SELECTOR_OFFSET_BORDER_WIDTH,
            tileSelectorRectBorderColor=TILE_SELECTOR_RECT_BORDER_COLOR,
            tileRectBorderColor=TILE_RECT_BORDER_COLOR,
            tileAvailableColor=TILE_AVAILABLE_COLOR,
            tileUnavailableColor=TILE_UNAVAILABLE_COLOR,
            tileFont=TILE_FONT,
            backgroundColor=BACKGROUND_COLOR,
            scoreboardSize2=SCOREBOARD_SIZE2,
            ownScoreboardPos=OWN_SCOREBOARD_POS,
            enemyScoreboardPos=ENEMY_SCOREBOARD_POS,
            scoreFont=SCORE_FONT,
            menuItemSelectorOffset=MENU_ITEM_SELECTOR_OFFSET,
        )

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

    def _handleSwitchOff(self):
        if self._goodbyeEvents is not None:
            for e in self._goodbyeEvents:
                self.pushInternalEvent(e.id, e.data)
        self._lastMovementCause = GUILayer._LAST_MOVEMENT_CAUSE_MOUSE
        self._internalMouseMoveOccurred = False
        self._lastMouseMovementTime = time.time()
        self._isAwaitingSwitchOff = False
        self._switchOffCountdownStart = None
        self._switchOffDelay = None
        self._goodbyeEvents = None
        self.__handleSwitchOff()

    def __handleSwitchOff(self):
        pass

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
                return self._handleMouseMovedEvent(event)
            else:
                self._internalMouseMoveOccurred = False

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

    def _onUpdate(self):
        pass

    def onUpdate(self):
        if self.isAwaitingSwitchOff() and self.isSwitchedOn():
            now = time.time()
            if self._switchOffCountdownStart + self._switchOffDelay < now:
                self.switchOff()
                return
        self._onUpdate()

    def scheduleSwitchOff(self, delay, goodbyeEvents=None):
        self._isAwaitingSwitchOff = True
        self._switchOffCountdownStart = time.time()
        self._switchOffDelay = delay
        self._goodbyeEvents = goodbyeEvents

    def isAwaitingSwitchOff(self):
        return self._isAwaitingSwitchOff
