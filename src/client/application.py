import sys # TODO: remove later
import pygame

from client import eventlist
from client.common.layer import LayerStack
from client.gui.layers.boardlayer import BoardLayer
from client.gui.layers.lobbylayer import LobbyLayer
from client.gui.layers.openroomlayer import OpenRoomLayer
from client.connection.layers.connectionlayer import ConnectionLayer


class GameApp:
    def __init__(self, screenSize):
        self._running = True
        self._eventSubscriptions = {}

        self._displayScreen = pygame.display.set_mode(screenSize)
        pygame.key.set_repeat(300, 100)

        connectionLayer = ConnectionLayer(sys.argv[1], int(sys.argv[2]), clientPollrate=15)
        boardGUILayer = BoardLayer()
        lobbyLayer = LobbyLayer()
        lobbyLayer.switchOn()
        openRoomLayer = OpenRoomLayer()
        self._layerStack = LayerStack([openRoomLayer, connectionLayer, boardGUILayer, lobbyLayer])
        self._quitGameInternalEvents = set([eventlist.LOBBYGUILAYER_QUITGAME_ID])

    def _handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    if layer.handleEvent(event):
                        break

    def run(self):
        for layer in self._layerStack:
            self._eventSubscriptions[layer.getID()] = set(layer.internalEventSubscriptions())

        clock = pygame.time.Clock()
        while self._running:
            clock.tick(30)
            self._handleEvents()

            stopRunning = False
            for layer in self._layerStack:
                if stopRunning:
                    break

                events = layer.emitEvents()
                for e in events:
                    if e.id in self._quitGameInternalEvents:
                        stopRunning = True

                    for l in self._layerStack:
                        if l.getID() != layer.getID() and\
                           e.id in self._eventSubscriptions[l.getID()]:
                            l.handleInternalEvent(e)

            if stopRunning:
                break

            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    layer.onUpdate()

            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    layer.onRender(self._displayScreen)
            pygame.display.update()
            pygame.display.flip()
