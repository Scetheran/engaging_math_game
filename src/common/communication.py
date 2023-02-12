import struct
import socket
import pickle
from contextlib import contextmanager


def prependLength(buffer):
    res = bytearray(struct.pack("!I", len(buffer)))
    res.extend(buffer)
    return res


class RetryDataFetch(Exception):
    pass


def recv_msg(sock: socket.socket, block=True):
    with setblocking_socket(sock, block) as sckt:
        rawMsglen = recvall(sckt, 4)
        if not rawMsglen:
            return None
        msglen = struct.unpack("!I", rawMsglen)[0]
        return recvall(sckt, msglen)


def recvall(sock: socket.socket, n):
    data = bytearray()
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        except socket.error as err:
            if err.errno == socket.EAGAIN or err.errno == socket.EWOULDBLOCK:
                raise RetryDataFetch()
            else:
                return None
    return data

@contextmanager
def setblocking_socket(sock, block):
    if not block:
        sock.setblocking(False)
    yield sock
    sock.setblocking(True)

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
