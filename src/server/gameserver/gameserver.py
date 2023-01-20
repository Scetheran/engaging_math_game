import time
import socket
import struct
import random
import multiprocessing
import selectors
import base64

from common import communication, gamedata


class GameRoom:
    def __init__(self, chan, id, ownerConn, tickRate) -> None:
        self._chan = chan
        self._roomId = id
        self._sleepDelay = 1 / tickRate
        self._p1Conn = ownerConn
        self._p2Conn = None
        self._run = False

    def waitForOpponent(self):
        self._p2Conn = self._chan.recv()
        self._chan.send(communication.ResponseCode.OK)
        self._chan.close()
        print("Opponent joined the game")

    def _prepareGame(self):
        self._p1ID = random.randint(1000, 9999)

        self._p2ID = random.randint(1000, 9999)
        while self._p1ID == self._p2ID:
            self._p2ID = random.random(1000, 9999)
        pass

        p1Heading = random.randint(0, 1)
        p1Turn = bool(random.randint(0, 1))

        p2Heading = 1 - p1Heading
        p2Turn = not p1Turn

        board = gamedata.GameBoard.generateBoard().data()
        startPos = board.index(gamedata.GameBoard.SpecialTile.SMILEY)
        (startY, startX) = divmod(startPos, 8)

        self._playerData = {
            self._p1ID: gamedata.PlayerData(0, 0, p1Turn, p1Heading, (startX, startY)),
            self._p2ID: gamedata.PlayerData(0, 0, p2Turn, p2Heading, (startX, startY)),
        }

        self._currentPlayerTurn = self._p1ID if p1Turn else self._p2ID
        self._currentBoardPos = (startX, startY)
        self._currentBoard = board

    def _handleRequest(self, playerConn, playerID, rawRequest):
        request = communication.parseMsg(rawRequest)
        if request.id == gamedata.Request.GET_BOARD_STATE and request.data == None:
            rawResponse = communication.buildMsg(
                (
                    communication.ResponseCode.OK,
                    gamedata.GameData(
                        self._playerData[playerID],
                        self._currentBoard,
                        gamedata.GameStatus.RUNNING,
                    ),
                )
            )
            playerConn.sendall(rawResponse)
        else:
            raise Exception()

    def runGame(self):
        self._prepareGame()

        selector = selectors.DefaultSelector()
        selector.register(
            self._p1Conn, selectors.EVENT_READ, (self._p1ID, self._p2Conn)
        )
        selector.register(
            self._p2Conn, selectors.EVENT_READ, (self._p2ID, self._p2Conn)
        )

        roomReadyMsg = communication.buildMsg(
            (communication.ResponseCode.ROOM_CREATED, None)
        )
        self._p1Conn.sendall(roomReadyMsg)
        self._p2Conn.sendall(roomReadyMsg)

        self._run = True
        while self._run:
            ready = selector.select()

            for key, _ in ready:
                playerId, opponentConn = key.data
                rawRequest = communication.recv_msg(key.fileobj)
                if rawRequest is None:
                    print(f"Player {playerId} terminated the connection. Exiting")
                    opponentConn.close()
                    self._run = False
                else:
                    try:
                        self._handleRequest(key.fileobj, playerId, rawRequest)
                    except:
                        print(f"Encountered an unexpected error")
                        self._run = False

            time.sleep(self._sleepDelay)


class GameServer:
    def __init__(self, address, port, tickRate):
        self._address = address
        self._port = port
        self._tickRate = tickRate
        self._semaphore = multiprocessing.Semaphore(100)
        self._openRooms = {}

    def _roomHandler(chan, id, sock, sem, tickRate):
        game = GameRoom(chan, id, sock, tickRate)
        game.waitForOpponent()
        game.runGame()
        sem.release()

    def _handleCreateRoom(self, conn, addr):
        if self._semaphore.acquire(block=False):
            (parent_conn, child_conn) = multiprocessing.Pipe(duplex=True)
            (ip, port) = addr
            roomId = socket.inet_aton(ip)
            roomId += struct.pack("!H", port)
            roomCode = base64.b32encode(roomId).decode().rstrip("= \n\r\t")
            pr = multiprocessing.Process(
                target=GameServer._roomHandler,
                args=(child_conn, roomCode, conn, self._semaphore, self._tickRate),
                daemon=True,
            )
            pr.start()
            self._openRooms[roomCode] = parent_conn
            print(f"Room code: {roomCode}")
            return communication.buildMsg((communication.ResponseCode.OK, roomCode))

        print("All available rooms are currently occupied")
        return communication.buildMsg((communication.ResponseCode.SERVER_FULL, None))

    def _handleJoinRoom(self, conn, roomCode):
        if roomCode not in self._openRooms:
            return communication.buildMsg(
                (communication.ResponseCode.WRONG_ROOM_ID, None)
            )

        pipe = self._openRooms[roomCode]
        pipe.send(conn)
        pipe.recv()
        pipe.close()
        self._openRooms.pop(roomCode)
        return communication.buildMsg((communication.ResponseCode.OK, None))

    def _handleNewConnection(self, conn, addr):
        rawRequest = communication.recv_msg(conn)
        if rawRequest is None:
            return
        request = communication.parseMsg(rawRequest)
        rawResponse = None
        if request.id == gamedata.Request.CREATE_ROOM and request.data is None:
            rawResponse = self._handleCreateRoom(conn, addr)
        elif request.id == gamedata.Request.ENTER_ROOM and request.data is not None:
            rawResponse = self._handleJoinRoom(conn, request.data)
        else:
            rawResponse = communication.buildMsg(
                (communication.ResponseCode.NOT_OK, None)
            )
        conn.sendall(rawResponse)
        conn.close()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._address, self._port))
            s.listen()
            print(f"Started server on {self._address}:{self._port}")
            while True:
                conn, addr = s.accept()
                print(f"Established connection with: {addr}")
                self._handleNewConnection(conn, addr)
