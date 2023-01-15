import struct
import socket
import pickle


def prependLength(buffer):
    res = bytearray(struct.pack("!I", len(buffer)))
    res.extend(buffer)
    return res


def recv_msg(sock: socket.socket):
    rawMsglen = recvall(sock, 4)
    if not rawMsglen:
        return None
    msglen = struct.unpack("!I", rawMsglen)[0]
    return recvall(sock, msglen)


def recvall(sock: socket.socket, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
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
