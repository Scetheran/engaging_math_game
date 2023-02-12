class InternalEvent:
    def __init__(self, id, data=None):
        self.id = id
        self.data = data


class GameAppLayer:
    def __init__(self, layerID):
        self._id = layerID
        self._isSwitchedOn = False
        self._pushedEvents = []

    def getID(self):
        return self._id

    def _handleSwitchOn(self):
        pass

    def _handleSwitchOff(self):
        pass

    def _subscribeToInternalEvents(self):
        return []

    def switchOn(self):
        self._isSwitchedOn = True
        self._pushedEvents = []
        self._handleSwitchOn()

    def switchOff(self):
        self._isSwitchedOn = False
        self._handleSwitchOff()

    def internalEventSubscriptions(self):
        return self._subscribeToInternalEvents()

    def isSwitchedOn(self):
        return self._isSwitchedOn

    def handleEvent(self, event):
        return False

    def handleInternalEvent(self, event):
        pass

    def pushInternalEvent(self, eventID, data=None):
        self._pushedEvents.append(InternalEvent(eventID, data))

    def onUpdate(self):
        pass

    def emitEvents(self):
        events = tuple(self._pushedEvents)
        self._pushedEvents.clear()
        return events

    def onRender(self, screen):
        pass


class LayerStack:
    def __init__(self, layers):
        self._layers = layers
        self._namesDict = dict()
        if self._layers:
            for (idx, layer) in enumerate(self._layers):
                self._namesDict[layer.getID()] = idx

    def getByID(self, layerName):
        return self._layers[self._namesDict[layerName]]

    def getByIdx(self, layerIdx):
        return self._layers[layerIdx]

    def __iter__(self):
        return iter(self._layers)
