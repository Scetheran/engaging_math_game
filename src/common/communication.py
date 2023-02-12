import struct
import socket
import pickle


def prependLength(buffer):
    res = bytearray(struct.pack("!I", len(buffer)))
    res.extend(buffer)
    return res


class RetryDataFetch(Exception):
    pass


def recv_msg(sock: socket.socket, block=True):
    rawMsglen = recvall(sock, 4, block)
    if not rawMsglen:
        return None
    msglen = struct.unpack("!I", rawMsglen)[0]
    return recvall(sock, msglen, block)


def recvall(sock: socket.socket, n, block=True):
    data = bytearray()
    while len(data) < n:
        try:
            packet = (
                sock.recv(n - len(data))
                if block
                else sock.recv(n - len(data), socket.MSG_DONTWAIT)
            )
            if not packet:
                return None
            data.extend(packet)
        except socket.error as err:
            if err.errno == socket.EAGAIN or err.errno == socket.EWOULDBLOCK:
                raise RetryDataFetch()
            else:
                return None
    return data


def buildMsg(obj):
    data = pickle.dumps(obj)
    data = prependLength(data)
    return data


def parseMsg(data):
    return pickle.loads(data)


class ResponseCode:
    OK = 0
    ROOM_CREATED = 1
    GAME_INTERRUPTED = 2
    GAME_OVER = 3
    SERVER_FULL = 4
    WRONG_ROOM_ID = 5
    NOT_OK = 6
