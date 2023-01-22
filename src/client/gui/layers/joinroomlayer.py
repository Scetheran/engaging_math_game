import pygame
from client import eventlist
from client.common.layer import InternalEvent
from client.gui.baseguilayer import GUILayer

class OpenRoomLayer(GUILayer):
    def __init__(self):
        super().__init__("joinroomgui.layer.id")
        self._gameConfig = self._generateGameConfig()

        self._infoMsgRect = pygame.Rect(self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
                                       self._gameConfig.screenCenterY - (3 * self._gameConfig.tileSize) // 2,
                                       8 * self._gameConfig.tileSize,
                                       self._gameConfig.tileSize)

        self._roomIDPromptRect = pygame.Rect(self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
                                       self._gameConfig.screenCenterY - (3 * self._gameConfig.tileSize) // 2,
                                       5 * self._gameConfig.tileSize,
                                       self._gameConfig.tileSize)
        self._roomIDPromptRectText = self._gameConfig.tileFont.render(f"Enter code:", True, self._gameConfig.tileRectBorderColor)
        self._roomIDInputFieldRect = pygame.Rect(self._gameConfig.screenCenterX + self._gameConfig.tileSize,
                                       self._gameConfig.screenCenterY - (3 * self._gameConfig.tileSize) // 2,
                                       3 * self._gameConfig.tileSize,
                                       self._gameConfig.tileSize)

        self._confirmCodeRect = pygame.Rect(self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
                                           self._gameConfig.screenCenterY,
                                           8 * self._gameConfig.tileSize,
                                           self._gameConfig.tileSize)
        self._confirmCodeRectText = self._gameConfig.tileFont.render(f"Confirm", True, self._gameConfig.tileRectBorderColor)


        self._goToLobbyRect = pygame.Rect(self._gameConfig.screenCenterX - 4 * self._gameConfig.tileSize,
                                           self._gameConfig.screenHeight - 2 * self._gameConfig.tileSize,
                                           8 * self._gameConfig.tileSize,
                                           self._gameConfig.tileSize)
        self._goToLobbyRectText = self._gameConfig.tileFont.render(f"Back", True, self._gameConfig.tileRectBorderColor)
        # offsetx, offsety = self._goToLobbyRect.topleft
        # self._goToLobbyInnerRect = pygame.Rect(
        #             offsetx
        #             + self._gameConfig.menuItemSelectorOffset,
        #             offsety
        #             + self._gameConfig.menuItemSelectorOffset,
        #             self._gameConfig.tileSize * 8
        #             - self._gameConfig.menuItemSelectorOffset * 2,
        #             self._gameConfig.tileSize
        #             - self._gameConfig.menuItemSelectorOffset * 2,
        #         )
        self._selectableRects = [(self._confirmCodeRect, self._confirmCodeRectText), (self._goToLobbyRect, self._goToLobbyRectText)]
        self._selectedRect = 0
        self._roomID = ""
        self._waitingToJoin = False
        self._errorMsg = None

    def _handleSwitchOn(self):
        self._selectedRect = 0
        self._roomID = ""
        self._waitingToJoin = False
        self._errorMsg = None
        self.pushInternalEvent(eventlist.JOINROOMGUILAYER_JOINROOM_ID)

    def _subscribeToInternalEvents(self):
        return [eventlist.LOBBYGUILAYER_TRANSJOINROOM_ID, eventlist.CONNECTIONLAYER_GAMEBEGAN_ID, eventlist.CONNECTIONLAYER_CONNLOST_ID, eventlist.CONNECTIONLAYER_UNEXPECTEDERROR_ID]

    def _handleKeyPressedEvent(self, event):
        if event.key == pygame.K_UP:
            self._selectedRect -= 1
        if event.key == pygame.K_DOWN:
            self._selectedRect += 1
        if event.key == pygame.K_LEFT:
            self._selectedRect -= 1
        if event.key == pygame.K_RIGHT:
            self._selectedRect += 1

        self._selectedRect = (len(self._selectableRects) + self._selectedRect) % len(self._selectableRects)

        if (event.key == pygame.K_RETURN and self._selectedRect == 1) or event.key == pygame.K_ESCAPE:
            self.pushInternalEvent(eventlist.JOINROOMGUILAYER_TRANSLOBBY_ID)
            if self._waitingToJoin:
                self.pushInternalEvent(eventlist.JOINROOMGUILAYER_CONNSHOULDCLOSE_ID)
            self.switchOff()

        if (event.key == pygame.K_RETURN and self._selectedRect == 0):
            if len(self._roomID) == 10 and self._roomID.isalnum():
                self.pushInternalEvent(eventlist.JOINROOMGUILAYER_JOINROOM_ID, self._roomID)
                self._waitingToJoin = True

        if event.unicode.isalnum():
            self._roomID += event.unicode
        return True

    def _handleMouseLBClickedEvent(self, event):
        if self._selectedRect == 1 and self._goToLobbyRect.collidepoint(*event.pos):
            self.pushInternalEvent(eventlist.JOINROOMGUILAYER_TRANSLOBBY_ID)
            if self._waitingToJoin:
                self.pushInternalEvent(eventlist.JOINROOMGUILAYER_CONNSHOULDCLOSE_ID)
            self.switchOff()

        if self._selectedRect == 0 and self._confirmCodeRect.collidepoint(*event.pos):
            if len(self._roomID) == 10 and self._roomID.isalnum():
                self.pushInternalEvent(eventlist.JOINROOMGUILAYER_JOINROOM_ID, self._roomID)
                self._waitingToJoin = True

        return True


    def _handleMouseMovedEvent(self, event):
        for (idx, (r, _)) in enumerate(self._selectableRects):
            if r.collidepoint(*event.pos):
                self._selectedRect = idx
        return True

    def handleInternalEvent(self, event):
        if event.id == eventlist.LOBBYGUILAYER_TRANSJOINROOM_ID:
            self.switchOn()
        elif event.id == eventlist.CONNECTIONLAYER_ROOMCREATED_ID and self.isSwitchedOn():
            self._roomID = event.data
        elif event.id == eventlist.CONNECTIONLAYER_GAMEBEGAN_ID and self.isSwitchedOn():
            self.pushInternalEvent(eventlist.OPENROOMGUILAYER_TRANSBOARDGUI_ID)
        elif event.id == eventlist.CONNECTIONLAYER_CONNLOST_ID and self.isSwitchedOn():
            self._errorMsg = "Connection Lost"
            self.scheduleSwitchOff(3, [InternalEvent(eventlist.JOINROOMGUILAYER_TRANSLOBBY_ID)])
        elif event.id == eventlist.CONNECTIONLAYER_UNEXPECTEDERROR_ID and self.isSwitchedOn():
            self._errorMsg = "Unexpected Error"
            self.scheduleSwitchOff(3, [InternalEvent(eventlist.JOINROOMGUILAYER_TRANSLOBBY_ID)])


    def _onRender(self, screen):
        screen.fill(self._gameConfig.backgroundColor)

        if self._errorMsg is not None:
            pass

