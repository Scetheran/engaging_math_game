import pygame
from client import eventlist
from client.common.layer import InternalEvent
from client.gui.baseguilayer import GUILayer


class OpenRoomLayer(GUILayer):
    def __init__(self):
        super().__init__("openroomgui.layer.id")
        self._gameConfig = self._generateGameConfig()

        self._roomIDRect = pygame.Rect(
            self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
            self._gameConfig.screenCenterY - (3 * self._gameConfig.tileSize) // 2,
            8 * self._gameConfig.tileSize,
            self._gameConfig.tileSize,
        )

        self._waitingOppRect = pygame.Rect(
            self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
            self._gameConfig.screenCenterY,
            8 * self._gameConfig.tileSize,
            self._gameConfig.tileSize,
        )

        self._goToLobbyRect = pygame.Rect(
            self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
            self._gameConfig.screenHeight - 2 * self._gameConfig.tileSize,
            8 * self._gameConfig.tileSize,
            self._gameConfig.tileSize,
        )
        self._goToLobbyRectText = self._gameConfig.tileFont.render(
            f"Back", True, self._gameConfig.tileRectBorderColor
        )
        offsetx, offsety = self._goToLobbyRect.topleft
        self._goToLobbyInnerRect = pygame.Rect(
            offsetx + self._gameConfig.menuItemSelectorOffset,
            offsety + self._gameConfig.menuItemSelectorOffset,
            self._gameConfig.tileSize * 8 - self._gameConfig.menuItemSelectorOffset * 2,
            self._gameConfig.tileSize - self._gameConfig.menuItemSelectorOffset * 2,
        )
        self._goToLobbySelected = False

        self._roomID = None
        self._errorMsg = None

    def _handleSwitchOn(self):
        self._goToLobbySelected = False
        self._roomID = None
        self._errorMsg = None
        self.pushInternalEvent(eventlist.OPENROOMGUILAYER_OPENROOM_ID)

    def _subscribeToInternalEvents(self):
        return [
            eventlist.LOBBYGUILAYER_TRANSOPENROOM_ID,
            eventlist.CONNECTIONLAYER_ROOMCREATED_ID,
            eventlist.CONNECTIONLAYER_GAMEBEGAN_ID,
            eventlist.CONNECTIONLAYER_CONNLOST_ID,
            eventlist.CONNECTIONLAYER_UNEXPECTEDERROR_ID,
            eventlist.CONNECTIONLAYER_SERVERDOWN_ID,
            eventlist.CONNECTIONLAYER_SERVERFULL_ID,
        ]

    def _handleKeyPressedEvent(self, event):
        if event.key == pygame.K_w or event.key == pygame.K_UP:
            self._goToLobbySelected = True
        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            self._goToLobbySelected = True
        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            self._goToLobbySelected = True
        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            self._goToLobbySelected = True

        if (
            event.key == pygame.K_RETURN and self._goToLobbySelected
        ) or event.key == pygame.K_ESCAPE:
            self.pushInternalEvent(eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID)
            self.pushInternalEvent(eventlist.OPENROOMGUILAYER_CONNSHOULDCLOSE_ID)
            self.switchOff()
        return True

    def _handleMouseLBClickedEvent(self, event):
        if self._goToLobbySelected and self._goToLobbyRect.collidepoint(*event.pos):
            self.pushInternalEvent(eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID)
            self.pushInternalEvent(eventlist.OPENROOMGUILAYER_CONNSHOULDCLOSE_ID)
            self.switchOff()
        return True

    def _handleMouseMovedEvent(self, event):
        if self._goToLobbyRect.collidepoint(*event.pos):
            self._goToLobbySelected = True
        else:
            self._goToLobbySelected = False
        return True

    def handleInternalEvent(self, event):
        if event.id == eventlist.LOBBYGUILAYER_TRANSOPENROOM_ID:
            self.switchOn()
        elif (
            event.id == eventlist.CONNECTIONLAYER_ROOMCREATED_ID and self.isSwitchedOn()
        ):
            self._roomID = event.data
        elif event.id == eventlist.CONNECTIONLAYER_GAMEBEGAN_ID and self.isSwitchedOn():
            self.pushInternalEvent(eventlist.OPENROOMGUILAYER_TRANSBOARDGUI_ID)
            self.switchOff()
        elif event.id == eventlist.CONNECTIONLAYER_CONNLOST_ID and self.isSwitchedOn():
            self._errorMsg = "Connection Lost"
            self.scheduleSwitchOff(
                3, [InternalEvent(eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID)]
            )
        elif (
            event.id == eventlist.CONNECTIONLAYER_UNEXPECTEDERROR_ID
            and self.isSwitchedOn()
        ):
            self._errorMsg = "Unexpected Error"
            self.scheduleSwitchOff(
                3, [InternalEvent(eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID)]
            )
        elif (
            event.id == eventlist.CONNECTIONLAYER_SERVERDOWN_ID and self.isSwitchedOn()
        ):
            self._errorMsg = "Server Unavailable"
            self.scheduleSwitchOff(
                3, [InternalEvent(eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID)]
            )
        elif (
            event.id == eventlist.CONNECTIONLAYER_SERVERFULL_ID and self.isSwitchedOn()
        ):
            self._errorMsg = "Server is full"
            self.scheduleSwitchOff(
                3, [InternalEvent(eventlist.OPENROOMGUILAYER_TRANSLOBBY_ID)]
            )

    def _onRender(self, screen):
        screen.fill(self._gameConfig.backgroundColor)

        pygame.draw.rect(
            screen,
            self._gameConfig.tileRectBorderColor,
            self._goToLobbyRect,
            self._gameConfig.tileBorderWidth,
            self._gameConfig.tileBorderRadius,
        )
        screen.blit(
            self._goToLobbyRectText,
            self._goToLobbyRectText.get_rect(center=self._goToLobbyRect.center),
        )
        if self._goToLobbySelected:
            pygame.draw.rect(
                screen,
                self._gameConfig.tileSelectorRectBorderColor,
                self._goToLobbyInnerRect,
                self._gameConfig.tileSelectorOffsetBorderWidth,
                self._gameConfig.tileBorderRadius,
            )

        if self.isAwaitingSwitchOff():
            roomIDPlaceholderError = self._gameConfig.tileFont.render(
                self._errorMsg, True, self._gameConfig.tileRectBorderColor
            )
            screen.blit(
                roomIDPlaceholderError,
                roomIDPlaceholderError.get_rect(center=self._roomIDRect.center),
            )
            return

        if self._roomID is not None:
            roomIDText = self._gameConfig.tileFont.render(
                f"Room code:  {self._roomID}",
                True,
                self._gameConfig.tileRectBorderColor,
            )
            screen.blit(roomIDText, roomIDText.get_rect(center=self._roomIDRect.center))
            waitingOppText = self._gameConfig.tileFont.render(
                "Waiting for opponent...", True, self._gameConfig.tileRectBorderColor
            )
            screen.blit(
                waitingOppText,
                waitingOppText.get_rect(center=self._waitingOppRect.center),
            )
            return

        roomIDPlaceholder = self._gameConfig.tileFont.render(
            self._roomID, True, self._gameConfig.tileRectBorderColor
        )
        screen.blit(
            roomIDPlaceholder,
            roomIDPlaceholder.get_rect(center=self._roomIDRect.center),
        )
