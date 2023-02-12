import random


class PlayerData:
    class Heading:
        ROWS = 1
        COLUMNS = 0

    def __init__(self, ownScore, enemyScore, turn, heading, lastPos) -> None:
        self.ownScore = ownScore
        self.enemyScore = enemyScore
        self.turn = turn
        self.heading = heading
        self.lastPos = lastPos


class GameStatus:
    RUNNING = 0
    OVER = 1


class GameData:
    def __init__(self, playerData, board, status) -> None:
        self.playerData = playerData
        self.board = board
        self.status = status


class GameBoard:
    class SpecialTile:
        EMPTY = 0xFFFFFFFF
        SMILEY = 0xFFFFFFFE

    def __init__(self, data: list) -> None:
        self._board = data

    def tileToStr(tileData):
        if tileData == GameBoard.SpecialTile.EMPTY:
            return ""
        elif tileData == GameBoard.SpecialTile.SMILEY:
            return ":)"

        return str(tileData)

    def getAt(self, x, y):
        return self._board[x + 8 * y]

    def setAt(self, x, y, value):
        self._board[x + 8 * y] = value

    def data(self):
        return self._board

    def generateBoard():
        board = [
            -10,
            -7,
            -6,
            -6,
            -5,
            -5,
            -4,
            -4,
            -4,
            -3,
            -3,
            -3,
            -2,
            -2,
            -2,
            -2,
            -1,
            -1,
            -1,
            -1,
            -1,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            3,
            4,
            4,
            4,
            4,
            5,
            6,
            6,
            6,
            6,
            6,
            6,
            6,
            6,
            7,
            7,
            7,
            8,
            8,
            10,
            15,
            GameBoard.SpecialTile.SMILEY,
        ]
        random.shuffle(board)
        return GameBoard(board)


class Request:
    GET_BOARD_STATE = 1
    MAKE_MOVE = 2
    CREATE_ROOM = 3
    ENTER_ROOM = 4

    def __init__(self, id, data=None) -> None:
        self.data = data
        self.id = id
