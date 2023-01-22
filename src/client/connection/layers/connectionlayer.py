
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
        self._clientType = None
        self._gamedata = None
        self._gameRunning = False
        self._roomCreated = False

    def _handleSwitchOn(self):
        self._client = gameclient.GameClient(self._serverAddress, self._serverPort, self._clientType ,self._pollrate)

    def _handleSwitchOff(self):
        if self._client is not None:
            self._client.shutdown()
            self._client = None
        self._clientType = None
        self._gamedata = None
        self._gameRunning = False
        self._roomCreated = False

    def _subscribeToInternalEvents(self):
        return [eventlist.BOARDGUILAYER_MOVEMADE_ID,
                eventlist.OPENROOMGUILAYER_OPENROOM_ID,
                eventlist.JOINROOMGUILAYER_JOINROOM_ID,
                eventlist.OPENROOMGUILAYER_CONNSHOULDCLOSE_ID]

    def _handleExceptions(self, stubFn, *stubFnArgs, **stubFnKwargs):
            try:
                res = stubFn(*stubFnArgs, **stubFnKwargs)
                return res
            except gameclient.NotPlayersTurn:
                pass
            except gameclient.IncorrectMove:
                pass
            except gameclient.RepeatActionException:
                pass
            # except gameclient.ConnectionLost:
            #     self.pushInternalEvent(eventlist.CONNECTIONLAYER_CONNLOST_ID)
            #     self.switchOff()
            except gameclient.ServerIsFull:
                self.pushInternalEvent(eventlist.CONNECTIONLAYER_SERVERFULL_ID)
                self.switchOff()
            except gameclient.WrongWroomID:
                self.pushInternalEvent(eventlist.CONNECTIONLAYER_WRONGROOMID_ID)
                self.switchOff()
            except gameclient.UnexpectedError:
               self.pushInternalEvent(eventlist.CONNECTIONLAYER_UNEXPECTEDERROR_ID)
               self.switchOff()
    pass

    def handleInternalEvent(self, event):
        if event.id == eventlist.BOARDGUILAYER_MOVEMADE_ID and self.switchOn():
            if self._client is None:
                return

            if self._gamedata is None:
                return

            if not self._gamedata.playerData.turn:
                return

            heading = self._gamedata.playerData.heading
            if self._gamedata.playerData.lastPos[heading] != event.data[heading]:
                return

            self._handleExceptions(self._client.takeTile, *event.data)

        elif event.id == eventlist.OPENROOMGUILAYER_OPENROOM_ID:
            self._clientType = gameclient.GameClientType(gameclient.GameClientType.CREATE_ROOM)
            self.switchOn()
        elif event.id == eventlist.JOINROOMGUILAYER_JOINROOM_ID:
            self._clientType = gameclient.GameClientType(gameclient.GameClientType.JOIN_ROOM, event.data)
            self._roomCreated = True
            self.switchOn()
        elif event.id == eventlist.OPENROOMGUILAYER_CONNSHOULDCLOSE_ID and self.isSwitchedOn():
            self.switchOff()

    def onUpdate(self):
        if self._client is None:
            return

        if not self._roomCreated:
            roomCode = self._handleExceptions(self._client.getRoomCode)
            if roomCode is not None:
                self.pushInternalEvent(eventlist.CONNECTIONLAYER_ROOMCREATED_ID, roomCode)
            else:
                return

        if not self._gameRunning:
            self._gameRunning = self._handleExceptions(self._client.isGameRunning)
            if self._gameRunning:
                self.pushInternalEvent(eventlist.CONNECTIONLAYER_GAMEBEGAN_ID)
            else:
                return

        self._gamedata = self._handleExceptions(self._client.gameData)
        if self._gamedata is not None:
            self.pushInternalEvent(eventlist.CONNECTIONLAYER_DATAUPDATED_ID, self._gamedata)




