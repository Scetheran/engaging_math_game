import pygame

from client.appcommon.dataobj import DataObject
from client.appcommon.applayer import LayerStack
from client.gui.layers.boardguilayer import BoardGUILayer


class GameApp:
    def __init__(self, screenSize):
        self._running = True
        self._displayScreen = pygame.display.set_mode(screenSize)
        pygame.key.set_repeat(300, 100)

        boardGUILayer = BoardGUILayer(self._getSharedData, self._switchLayer)
        boardGUILayer.turnOn()
        self._layerStack = LayerStack([boardGUILayer])

    def _handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    if layer.handleEvent(event):
                        break

    def _getSharedData(self, name):
        if name not in self._sharedData:
            return None

        return self._sharedData[name]

    def _switchLayer(self, layerName, action):
        if action == "on":
            self._layerStack.getByName(layerName).turnOn()
        if action == "off":
            self._layerStack.getByName(layerName).turnOff()

    def run(self):
        while self._running:
            self._handleEvents()
            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    layer.onUpdate()

            for layer in self._layerStack:
                if layer.isSwitchedOn():
                    layer.onRender(self._displayScreen)
            pygame.display.update()
            pygame.display.flip()

        for layer in self._layerStack:
            if layer.isSwitchedOn():
                layer.turnOff()
