
from client.common.layer import GameAppLayer
from client import eventlist
from .. import gameclient

class ConnectionLayer(GameAppLayer):
    def __init__(self, serverAddress, serverPort, clientPollrate=15):
        super().__init__("connection.layer.id")
        self._client = None
        self._serverAddress = serverAddress
        self._serverPort = serverPort
        self._pollrate = clientPollrate
        self._newClientType = None
        self._gamedata = None

    def _handleSwitchOn(self):
        self._client = gameclient.GameClient(self._serverAddress, self._serverPort, self._newClientType ,self._pollrate)

    def _handleSwitchOff(self):
        self._client.shutdown()
        self._client = None

    def _subscribeToInternalEvents(self):
        return [eventlist.BOARDGUILAYER_MOVEMADE_ID,
                eventlist.LOBBYGUILAYER_JOINROOM_ID,
                eventlist.LOBBYGUILAYER_OPENROOM_ID]

    def handleInternalEvent(self, event):
        if event.id == eventlist.BOARDGUILAYER_MOVEMADE_ID:
            if self._gamedata is None:
                return

            if not self._gamedata.playerData.turn:
                return

            heading = self._gamedata.playerData.heading
            if self._gamedata.playerData.lastPos[heading] != event.data[heading]:
                return

            if self._client is not None:
                try:
                    self._client.takeTile(*event.data)
                except gameclient.IncorrectMove:
                    pass
                except gameclient.NotPlayersTurn:
                    pass
                except gameclient.RepeatActionException:
                    pass
                except gameclient.ConnectionLost:
                    self.pushInternalEvent(eventlist.CONNECTIONLAYER_CONNLOST_ID)

        elif event.id == eventlist.LOBBYGUILAYER_OPENROOM_ID:
            self._newClientType = gameclient.GameClientType(gameclient.GameClientType.CREATE_ROOM)
            self.switchOn()
        elif event.id == eventlist.LOBBYGUILAYER_JOINROOM_ID:
            self._newClientType = gameclient.GameClientType(gameclient.GameClientType.JOIN_ROOM, event.data)
            self.switchOn()

    def onUpdate(self):
        if self._client is None:
            return
        try:
            self._gamedata = self._client.gameData()
            if self._gamedata is not None:
                self.pushInternalEvent(eventlist.CONNECTIONLAYER_DATAUPDATED_ID, self._gamedata)
        except gameclient.IncorrectMove:
            pass
        except gameclient.NotPlayersTurn:
            pass
        except gameclient.RepeatActionException:
            pass
        except gameclient.ConnectionLost:
            self.pushInternalEvent(eventlist.CONNECTIONLAYER_CONNLOST_ID)



