import sys # TODO: remove later
import pygame
from client.gui.baseguilayer import GUILayer
from client import eventlist
from common.gamedata import GameBoard, PlayerData


class BoardLayer(GUILayer):
    def __init__(self):
        super().__init__("boardgui.layer.id")
        self._handleSwitchOn()
        self._gameConfig = self._generateGameConfig()

    def _handleKeyPressedEvent(self, event):
        if event.key == pygame.K_w or event.key == pygame.K_UP:
            self._selectorRow -= 1
        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            self._selectorRow += 1
        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            self._selectorColumn -= 1
        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            self._selectorColumn += 1

        self._selectorColumn = (8 + self._selectorColumn) % 8
        self._selectorRow = (8 + self._selectorRow) % 8

        if event.key == pygame.K_j:
            self.pushInternalEvent(eventlist.OPENROOMGUILAYER_OPENROOM_ID, sys.argv[3])

        if event.key == pygame.K_RETURN:
            self.pushInternalEvent(eventlist.BOARDGUILAYER_MOVEMADE_ID, (self._selectorColumn, self._selectorRow))
        return True

    def _handleSwitchOn(self):
        self._selectorRow = 0
        self._selectorColumn = 0
        self._rects = None
        self._selectorInnerRect = None
        self._selectorOuterRect = None
        self._tileBorderColor = None
        self._gameData = None

    def _handleMouseLBClickedEvent(self, event):
        if self._selectorOuterRect is not None:
            if self._selectorOuterRect[0].collidepoint(*event.pos):
                self.pushInternalEvent(eventlist.BOARDGUILAYER_MOVEMADE_ID, (self._selectorColumn, self._selectorRow))
        return True

    def _onUpdate(self):
        if self._gameData is None:
            return
        offsetx = (
            self._gameConfig.screenCenterX
            - 4 * self._gameConfig.tileSize
            - int(3.5 * self._gameConfig.tileSpacing)
        )
        offsety = (
            self._gameConfig.screenCenterY
            - 4 * self._gameConfig.tileSize
            - int(3.5 * self._gameConfig.tileSpacing)
        )

        turn = self._gameData.playerData.turn
        heading = self._gameData.playerData.heading
        heading = heading if turn else (1 - heading)

        if heading == PlayerData.Heading.ROWS:
            playRow = self._gameData.playerData.lastPos[heading]
            playColumn = -1
        else:
            playRow = -1
            playColumn = self._gameData.playerData.lastPos[heading]

        self._rects = []
        for column in range(8):
            for row in range(8):
                r = pygame.Rect(
                    offsetx
                    + column
                    * (self._gameConfig.tileSize + self._gameConfig.tileSpacing),
                    offsety
                    + row * (self._gameConfig.tileSize + self._gameConfig.tileSpacing),
                    self._gameConfig.tileSize,
                    self._gameConfig.tileSize,
                )
                tileBorderColor = self._gameConfig.tileRectBorderColor

                if column == playColumn or row == playRow:
                    if turn:
                        tileBorderColor = self._gameConfig.tileAvailableColor
                    else:
                        tileBorderColor = self._gameConfig.tileUnavailableColor

                if (
                    self.lastMovementCause() == GUILayer._LAST_MOVEMENT_CAUSE_MOUSE
                    and r.collidepoint(pygame.mouse.get_pos())
                ):
                    self._selectorRow = row
                    self._selectorColumn = column

                if column == self._selectorColumn and row == self._selectorRow:
                    self.hideMouseAtPos(r.center)

                    innerRect = pygame.Rect(
                        offsetx
                        + self._gameConfig.tileSelectorOffset
                        + column
                        * (self._gameConfig.tileSize + self._gameConfig.tileSpacing),
                        offsety
                        + self._gameConfig.tileSelectorOffset
                        + row
                        * (self._gameConfig.tileSize + self._gameConfig.tileSpacing),
                        self._gameConfig.tileSize
                        - self._gameConfig.tileSelectorOffset * 2,
                        self._gameConfig.tileSize
                        - self._gameConfig.tileSelectorOffset * 2,
                    )
                    self._selectorInnerRect = (
                        innerRect,
                        self._gameConfig.tileSelectorRectBorderColor,
                        column,
                        row
                    )
                    self._selectorOuterRect = (r, tileBorderColor, column, row)
                else:
                    self._rects.append((r, tileBorderColor, column, row))

    def _onRender(self, screen):
        screen.fill(self._gameConfig.backgroundColor)
        if self._gameData is None:
            return

        for (r, color, x, y) in self._rects:
            pygame.draw.rect(
                screen,
                color,
                r,
                self._gameConfig.tileBorderWidth,
                self._gameConfig.tileBorderRadius,
            )
            text = self._gameConfig.tileFont.render(
                GameBoard.tileToStr(self._gameData.board.getAt(x, y)), True, self._gameConfig.tileRectBorderColor
            )
            screen.blit(text, text.get_rect(center=r.center))

        pygame.draw.rect(
            screen,
            self._selectorOuterRect[1],
            self._selectorOuterRect[0],
            self._gameConfig.tileSelectedBorderWidth,
            self._gameConfig.tileBorderRadius,
        )
        pygame.draw.rect(
            screen,
            self._selectorInnerRect[1],
            self._selectorInnerRect[0],
            self._gameConfig.tileSelectorOffsetBorderWidth,
            self._gameConfig.tileBorderRadius,
        )
        text = self._gameConfig.tileFont.render(
            GameBoard.tileToStr(self._gameData.board.getAt(self._selectorOuterRect[2], self._selectorOuterRect[3])), True, self._gameConfig.tileRectBorderColor
        )
        screen.blit(text, text.get_rect(center=self._selectorOuterRect[0].center))

        ownScoreRect = pygame.Rect(*self._gameConfig.ownScoreboardPos, *self._gameConfig.scoreboardSize2)
        pygame.draw.rect(screen, self._gameConfig.tileRectBorderColor, ownScoreRect, self._gameConfig.tileBorderWidth, self._gameConfig.tileBorderRadius)
        ownScore = self._gameConfig.scoreFont.render(f"YOU: {self._gameData.playerData.ownScore}", True, self._gameConfig.tileRectBorderColor)
        screen.blit(ownScore, ownScore.get_rect(center=ownScoreRect.center))

        enemyScoreRect = pygame.Rect(*self._gameConfig.enemyScoreboardPos, *self._gameConfig.scoreboardSize2)
        pygame.draw.rect(screen, self._gameConfig.tileRectBorderColor, enemyScoreRect, self._gameConfig.tileBorderWidth, self._gameConfig.tileBorderRadius)
        enemyScore = self._gameConfig.scoreFont.render(f"OPP: {self._gameData.playerData.enemyScore}", True, self._gameConfig.tileRectBorderColor)
        screen.blit(enemyScore, enemyScore.get_rect(center=enemyScoreRect.center))

        pygame.display.update()

    def _subscribeToInternalEvents(self):
        return [eventlist.CONNECTIONLAYER_DATAUPDATED_ID]

    def handleInternalEvent(self, event):
        if event.id == eventlist.CONNECTIONLAYER_DATAUPDATED_ID:
            self._gameData = event.data