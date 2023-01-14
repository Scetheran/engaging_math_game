import pickle
import socket
import threading

from ...common import communication
from ...common import gamedata


class GameConnectionStub:
    def __init__(self, remoteConn: socket.socket) -> None:
        self._conn = remoteConn

    def _request(self, id, data=None):
        requestMsg = pickle.dumps(gamedata.RequestData(id, data))
        requestMsg = communication.prependLength(requestMsg)
        self._remoteConn.sendall(requestMsg)
        response = communication.recv_msg(self._remoteConn)
        response = pickle.loads(response)
        return response

    def getGameData(self):
        return self._request(gamedata.RequestData.GET_BOARD_STATE)

    def takeTile(self, x, y):
        return self._request(gamedata.RequestData.MAKE_MOVE, (x, y))

    def createRoom(self):
        response = self._request(gamedata.RequestData.CREATE_ROOM)
        if response[0] == communication.ResponseCode.OK:

            def waitForOpponent():
                resp = communication.recv_msg(self._remoteConn)
                resp = pickle.loads(resp)
                return resp

            self.waitForOpponent = waitForOpponent
        else:
            pass

        return response

    def enterRoom(self, roomCode):
        return self._request(gamedata.RequestData.ENTER_ROOM, roomCode)


_GAME_CLIENT_LOCK = threading.Lock()


class RepeatActionException(Exception):
    pass


class GameClient:

    _MAX_ERRORS = 10

    def __init__(self, address, port, pollRate):
        self._pollerThread = None
        self._shutdownPoller = False

        self._cachedData = None
        self._takeTile = None
        self._createRoom = False
        self._joinRoom = None

    def gameData(self):
        with _GAME_CLIENT_LOCK:
            return self._cachedData

    def takeTile(self, x, y):
        with _GAME_CLIENT_LOCK:
            if self._takeTile is not None:
                raise RepeatActionException()
            self._takeTile = (x, y)

    def createRoom(self):
        with _GAME_CLIENT_LOCK:
            if self._createRoom:
                raise RepeatActionException()
            self._createRoom = True

    def joinRoom(self, roomCode):
        with _GAME_CLIENT_LOCK:
            if self._joinRoom is not None:
                raise RepeatActionException()
            self._joinRoom = roomCode
