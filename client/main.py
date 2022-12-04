import sys
import time
import socket
import random

(HOST, PORT) = (sys.argv[1], sys.argv[2])  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"Connecting to server: {HOST}:{PORT}")
    s.connect((sys.argv[1], sys.argv[2]))
    while True:
        num = random.randint(0, 100000)
        msg = f"Random number message: {num}"
        print(f"Sending msg: '{msg}'")
        #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.sendall(msg.encode())
        time.sleep(0.3)