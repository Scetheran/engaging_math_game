import os
import sys
import time
import queue
import socket
import struct
import errno
import threading
import random
import multiprocessing
import multiprocessing.reduction
import selectors

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from common import communication, gamedata

(HOST, PORT) = (
    sys.argv[1],
    int(sys.argv[2]),
)  # Port to listen on (non-privileged ports are > 1023)


def roomHandler(chan, sock, id, sem):
    game = GameRoom(chan, id, sock, 30)
    game.waitForOpponent()
    game.runGame()
    sem.release()


class GameRoom:
    def __init__(self, chan, id, ownerConn, tickrate) -> None:
        self._chan = chan
        self._roomId = id
        self._sleepDelay = 1 / tickrate
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
                    gamedata.GameData(self._playerData[playerID], self._currentBoard),
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
        print(roomReadyMsg)
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


def main():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

    openRooms = {}
    sem = multiprocessing.Semaphore(100)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Starting server on {HOST}:{PORT}")
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            print(f"Established connection with: {addr}")

            msg = conn.recv(3)
            print(msg)
            if msg == b"opn":
                if sem.acquire(block=False):
                    (parent_conn, child_conn) = multiprocessing.Pipe(duplex=True)
                    (ip, port) = addr
                    roomId = socket.inet_aton(ip)
                    roomId += struct.pack("!H", port)
                    roomId = roomId.hex()
                    pr = multiprocessing.Process(
                        target=roomHandler,
                        args=(child_conn, conn, roomId, sem),
                        daemon=True,
                    )
                    pr.start()
                    conn.close()
                    openRooms[roomId] = parent_conn
                    print("sent sock obj: {!r}".format(conn))
                    print(f"Room id: {roomId}")
                else:
                    print("All available rooms are currently occupied")
                    conn.sendall("All available rooms are currently occupied".encode())
                    conn.close()

            elif msg == b"ent":
                roomId = conn.recv(1024)
                roomId = roomId.decode("utf-8")
                if roomId not in openRooms:
                    conn.sendall("Wrong room ID".encode())
                    conn.close()
                else:
                    pipe = openRooms[roomId]
                    pipe.send(conn)
                    conn.close()
                    resp = pipe.recv()
                    if resp == 200:
                        pipe.close()
                        openRooms.pop(roomId)


if __name__ == "__main__":
    sys.exit(main())
