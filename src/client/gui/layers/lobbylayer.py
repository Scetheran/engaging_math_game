import pygame

from client.common.layer import InternalEvent
from client.gui.baseguilayer import GUILayer
from client import eventlist

class LobbyLayer(GUILayer):
    def __init__(self):
        super().__init__("lobbygui.layer.id")
        self._gameConfig = self._generateGameConfig()

        self._openRoomRect = pygame.Rect(self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
                                         self._gameConfig.screenCenterY - (5 * self._gameConfig.tileSize) // 2,
                                         8 * self._gameConfig.tileSize,
                                         self._gameConfig.tileSize)

        self._openRoomRectText = self._gameConfig.tileFont.render("Create new room", True, self._gameConfig.tileRectBorderColor)

        self._joinRoomRect = pygame.Rect(self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
                                         self._gameConfig.screenCenterY - self._gameConfig.tileSize,
                                         8 * self._gameConfig.tileSize,
                                         self._gameConfig.tileSize)
        self._joinRoomRectText = self._gameConfig.tileFont.render("Join Existing Room", True, self._gameConfig.tileRectBorderColor)

        self._quitGameRect = pygame.Rect(self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
                                         self._gameConfig.screenCenterY + self._gameConfig.tileSize // 2,
                                         8 * self._gameConfig.tileSize,
                                         self._gameConfig.tileSize)
        self._quitGameRectText = self._gameConfig.tileFont.render("Quit Game", True, self._gameConfig.tileRectBorderColor)
        self._rects = [(self._openRoomRect, self._openRoomRectText), (self._joinRoomRect, self._joinRoomRectText) , (self._quitGameRect, self._quitGameRectText)]
        self._selectedRect = 0

        self._events = [eventlist.LOBBYGUILAYER_TRANSOPENROOM_ID, eventlist.LOBBYGUILAYER_TRANSJOINROOM_ID, eventlist.LOBBYGUILAYER_QUITGAME_ID]

    def _handleSwitchOn(self):
        self._selectedRect = 0

    def _subscribeToInternalEvents(self):
        return [eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID]

    def handleInternalEvent(self, event):
        if event.id == eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID:
            self.switchOn()

    def _handleKeyPressedEvent(self, event):
        if event.key == pygame.K_w or event.key == pygame.K_UP:
            self._selectedRect -= 1
        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            self._selectedRect += 1
        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            self._selectedRect -= 1
        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            self._selectedRect += 1

        self._selectedRect = (len(self._rects) + self._selectedRect) % len(self._rects)

        if event.key == pygame.K_RETURN:
            self.pushInternalEvent(self._events[self._selectedRect])
            self.switchOff()

        return True

    def _handleMouseLBClickedEvent(self, event):
        if self._rects[self._selectedRect][0].collidepoint(*event.pos):
            self.pushInternalEvent(self._events[self._selectedRect])
            self.switchOff()
        return True

    def _onUpdate(self):
        for (idx, (r, _)) in enumerate(self._rects):
            if (
                self.lastMovementCause() == GUILayer._LAST_MOVEMENT_CAUSE_MOUSE
                and r.collidepoint(pygame.mouse.get_pos())
                ):
                    self._selectedRect = idx

    def _onRender(self, screen):
        screen.fill(self._gameConfig.backgroundColor)
        for (idx, (r, text)) in enumerate(self._rects):
            pygame.draw.rect(screen, self._gameConfig.tileRectBorderColor, r, self._gameConfig.tileBorderWidth, self._gameConfig.tileBorderRadius)
            screen.blit(text, text.get_rect(center=r.center))

            offsetx, offsety = r.topleft
            if self._selectedRect == idx:
                innerRect = pygame.Rect(
                    offsetx
                    + self._gameConfig.menuItemSelectorOffset,
                    offsety
                    + self._gameConfig.menuItemSelectorOffset,
                    self._gameConfig.tileSize * 8
                    - self._gameConfig.menuItemSelectorOffset * 2,
                    self._gameConfig.tileSize
                    - self._gameConfig.menuItemSelectorOffset * 2,
                )
                pygame.draw.rect(screen, self._gameConfig.tileSelectorRectBorderColor, innerRect, self._gameConfig.tileSelectorOffsetBorderWidth, self._gameConfig.tileBorderRadius)

        pygame.display.update()

