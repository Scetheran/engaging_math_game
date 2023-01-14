import os
import sys
import time
import socket
import random
import threading
import selectors

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from common import communication, gamedata

(HOST, PORT) = (sys.argv[1], int(sys.argv[2]))  # The port used by the server


def createClient():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to server: {HOST}:{PORT}")
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((HOST, PORT))
        print(f"Sending msg: {sys.argv[3].encode()}")
        s.sendall(sys.argv[3].encode())
        rawResp = communication.recv_msg(s)
        (respCode, gameData) = communication.parseMsg(rawResp)
        if respCode != communication.ResponseCode.ROOM_CREATED:
            print("Received wrong response during room creation")
            return

        while True:
            start = time.time_ns()
            rawMsg = communication.buildMsg(
                gamedata.Request(gamedata.Request.GET_BOARD_STATE, None)
            )
            s.sendall(rawMsg)
            rawResp = communication.recv_msg(s)
            (respCode, gameData) = communication.parseMsg(rawResp)
            if respCode != communication.ResponseCode.OK:
                print("Error while polling server for game state")
                return
            end = time.time_ns()
            print(f"Time taken: {end-start}ns")
            time.sleep(0.0666)


if __name__ == "__main__":
    createClient()
