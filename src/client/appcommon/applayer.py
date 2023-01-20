class GameAppLayer:
    def __init__(self, name, getSharedDataCallback=None, switchLayerCallback=None):
        self._name = name
        self._dataCallback = getSharedDataCallback
        self._switchLayerCallback = switchLayerCallback
        self._isSwitchedOn = False

    def getName(self):
        return self._name

    def _handleTurnOn(self):
        pass

    def _handleTurnOff(self):
        pass

    def turnOn(self):
        self._isSwitchedOn = True
        self._handleTurnOn()

    def turnOff(self):
        self._isSwitchedOn = False
        self._handleTurnOff()

    def isSwitchedOn(self):
        return self._isSwitchedOn

    def handleEvent(self, event):
        return False

    def onUpdate(self):
        pass

    def onRender(self, screen):
        pass


class LayerStack:
    def __init__(self, layers):
        self._layers = layers
        self._namesDict = dict()
        if self._layers:
            for (idx, layer) in enumerate(self._layers):
                self._namesDict[layer.getName()] = idx

    def getByName(self, layerName):
        return self._layers[self._namesDict[layerName]]

    def getByIdx(self, layerIdx):
        return self._layers[layerIdx]

    def __iter__(self):
        return iter(self._layers)
