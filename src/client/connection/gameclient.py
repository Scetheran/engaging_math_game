import sys
import time
import pickle
import socket
import threading

from common import communication
from common import gamedata


class GameConnectionStub:
    def __init__(self, remoteConn: socket.socket) -> None:
        self._conn = remoteConn

    def _request(self, id, data=None):
        requestMsg = pickle.dumps(gamedata.Request(id, data))
        requestMsg = communication.prependLength(requestMsg)
        self._conn.sendall(requestMsg)
        response = communication.recv_msg(self._conn)
        if response is None:
            raise ConnectionLost()
        response = pickle.loads(response)
        return response

    def getGameData(self):
        return self._request(gamedata.Request.GET_BOARD_STATE)

    def takeTile(self, x, y):
        return self._request(gamedata.Request.MAKE_MOVE, (x, y))

    def createRoom(self):
        return self._request(gamedata.Request.CREATE_ROOM)

    def enterRoom(self, roomCode):
        return self._request(gamedata.Request.ENTER_ROOM, roomCode)

    def checkIfRoomIsReady(self):
        resp = communication.recv_msg(self._conn, block=False)
        if resp is None:
            raise ConnectionLost()
        resp = pickle.loads(resp)
        return resp


_GAME_CLIENT_LOCK = threading.Lock()


class RepeatActionException(Exception):
    pass


class NotPlayersTurn(Exception):
    pass


class IncorrectMove(Exception):
    pass


class ConnectionLost(Exception):
    pass


class ServerUnavailable(Exception):
    pass


class ServerIsFull(Exception):
    pass


class WrongWroomID(Exception):
    pass


class UnexpectedError(Exception):
    pass


class GameClientType:
    JOIN_ROOM = 1
    CREATE_ROOM = 2

    def __init__(self, clientType, data=None):
        self.type = clientType
        self.data = data


class GameClient:
    def __init__(self, address, port, clientType, pollRate):
        self._cachedData = None
        self._takeTile = None
        self._roomCode = None
        self._exc_info = None
        self._gameIsRunning = False

        self._pollerThread = threading.Thread(
            target=self._threadFn,
            args=(address, port, pollRate, clientType),
            daemon=True,
        )
        self._shutdownPoller = False
        self._pollerThread.start()

    def _threadFn(self, address, port, pollRate, clientType):
        try:
            pollInterval = 1 / pollRate
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.connect((address, port))

                stub = GameConnectionStub(s)

                if clientType.type == GameClientType.CREATE_ROOM:
                    respCode, res = stub.createRoom()
                    if respCode == communication.ResponseCode.SERVER_FULL:
                        raise ServerIsFull()
                    elif respCode != communication.ResponseCode.OK:
                        raise UnexpectedError()
                    with _GAME_CLIENT_LOCK:
                        self._roomCode = res
                    while True:
                        with _GAME_CLIENT_LOCK:
                            if self._shutdownPoller:
                                return
                        try:
                            respCode, res = stub.checkIfRoomIsReady()
                            if respCode != communication.ResponseCode.ROOM_CREATED:
                                raise UnexpectedError()
                            break
                        except communication.RetryDataFetch:
                            time.sleep(pollInterval)

                elif clientType.type == GameClientType.JOIN_ROOM:
                    respCode, _ = stub.enterRoom(clientType.data)
                    if respCode == communication.ResponseCode.WRONG_ROOM_ID:
                        raise WrongWroomID()
                    elif respCode != communication.ResponseCode.OK:
                        raise UnexpectedError()
                    with _GAME_CLIENT_LOCK:
                        self._roomCode = clientType.data
                    while True:
                        with _GAME_CLIENT_LOCK:
                            if self._shutdownPoller:
                                return
                        try:
                            respCode, res = stub.checkIfRoomIsReady()
                            if respCode != communication.ResponseCode.ROOM_CREATED:
                                raise UnexpectedError()
                            break
                        except communication.RetryDataFetch:
                            time.sleep(pollInterval)

                with _GAME_CLIENT_LOCK:
                    self._gameIsRunning = True

                while True:
                    with _GAME_CLIENT_LOCK:
                        if self._shutdownPoller:
                            return

                    respCode, res = stub.getGameData()
                    if respCode == communication.ResponseCode.OK:
                        with _GAME_CLIENT_LOCK:
                            self._cachedData = res
                    else:
                        raise UnexpectedError()

                    move = None
                    with _GAME_CLIENT_LOCK:
                        if self._takeTile is not None:
                            move = self._takeTile

                    if move is not None:
                        (x, y) = move
                        respCode, res = stub.takeTile(x, y)
                        with _GAME_CLIENT_LOCK:
                            self._takeTile = None
                        if respCode == communication.ResponseCode.NOT_OK:
                            raise IncorrectMove()

                    time.sleep(pollInterval)
        except socket.error:
            try:
                raise ServerUnavailable()
            except Exception:
                with _GAME_CLIENT_LOCK:
                    self._exc_info = sys.exc_info()
        except Exception:
            with _GAME_CLIENT_LOCK:
                self._exc_info = sys.exc_info()

    def isGameRunning(self):
        with _GAME_CLIENT_LOCK:
            if self._exc_info is not None:
                raise self._exc_info[1].with_traceback(self._exc_info[2])
            return self._gameIsRunning

    def gameData(self):
        with _GAME_CLIENT_LOCK:
            if self._exc_info is not None:
                raise self._exc_info[1].with_traceback(self._exc_info[2])
            return self._cachedData

    def takeTile(self, x, y):
        with _GAME_CLIENT_LOCK:
            if self._exc_info is not None:
                raise self._exc_info[1].with_traceback(self._exc_info[2])
            if not self._cachedData.playerData.turn:
                raise NotPlayersTurn()
            if self._takeTile is not None:
                raise RepeatActionException()
            self._takeTile = (x, y)

    def getRoomCode(self):
        with _GAME_CLIENT_LOCK:
            if self._exc_info is not None:
                raise self._exc_info[1].with_traceback(self._exc_info[2])
            return self._roomCode

    def shutdown(self):
        with _GAME_CLIENT_LOCK:
            self._shutdownPoller = True
        if self._pollerThread.is_alive():
            self._pollerThread.join()
