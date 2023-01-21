import sys # TODO: remove later
import pygame

from client.common.layer import LayerStack
from client.gui.layers.boardguilayer import BoardGUILayer
from client.connection.layers.connectionlayer import ConnectionLayer


class GameApp:
    def __init__(self, screenSize):
        self._running = True
        self._eventSubscriptions = {}

        self._displayScreen = pygame.display.set_mode(screenSize)
        pygame.key.set_repeat(300, 100)

        connectionLayer = ConnectionLayer(sys.argv[1], int(sys.argv[2]), clientPollrate=15)
        boardGUILayer = BoardGUILayer()
        boardGUILayer.switchOn()
        self._layerStack = LayerStack([connectionLayer, boardGUILayer])

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
            for layer in self._layerStack:
                events = layer.emitEvents()
                for e in events:
                    for l in self._layerStack:
                        if l.getID() != layer.getID() and\
                           e.id in self._eventSubscriptions[l.getID()]:
                            l.handleInternalEvent(e)

            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    layer.onUpdate()

            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    layer.onRender(self._displayScreen)
            pygame.display.update()
            pygame.display.flip()

        for layer in self._layerStack:
            layer.switchOff()
