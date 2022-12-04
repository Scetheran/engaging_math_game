import sys
import time
import queue
import socket
import threading
import selectors


(HOST, PORT) = (sys.argv[1], sys.argv[2]) # Port to listen on (non-privileged ports are > 1023)

NEW_CONNECTIONS_QUEUE = queue.Queue(maxsize=0)
DROP_CONNECTIONS_QUEUE = queue.Queue(maxsize=0)
PROCESSING_QUEUE = queue.Queue(maxsize=0)

def serverThreadFn(connectionsQueue):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Starting server on {HOST}:{PORT}")
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            print(f"Established connection with: {addr}")
            connectionsQueue.put((conn, addr))

def selectorThreadFn(connectionsQueue, processingQueue, dropQueue):
    epollSelector = selectors.DefaultSelector()
    eventMaskMapping = {
        selectors.EVENT_READ : "EVENT_READ",
        selectors.EVENT_WRITE : "EVENT_WRITE",
        selectors.EVENT_WRITE | selectors.EVENT_WRITE : "EVENT_READ+WRITE"
    }

    while True:
        # Try to accept a new connection
        try:
            sock, addr = connectionsQueue.get(block=False)

            epollSelector.register(sock, selectors.EVENT_READ, addr)
            print(f"Registered a new client: {addr}")
        except queue.Empty:
            pass

        try:
            sock, addr = dropQueue.get(block=False)

            epollSelector.unregister(sock)
            print(f"Unregistered a new client: {addr}")
        except queue.Empty:
            pass


        ready = epollSelector.select(timeout=1)

        print(f"Received messages: {len(ready)}")
        for key, mask in ready:
            #print(f"Client event: {selectors.EVENT_WRITE}, {selectors.EVENT_READ}, {mask}")
            processingQueue.put((key.fileobj, key.data, mask))

        #print("=========================================\n\n\n\n\n\n")
        time.sleep(0.01)


def consumerThreadFn(processingQueue, dropQueue):
    while True:
        try:
            (sock, addr, mask) = processingQueue.get(block=True, timeout=1)
            data = sock.recv(1024)

            if data:
                pass
                #print(f"Received data from client {addr}: {data}")
            else:
                dropQueue.put((sock, addr))
        except queue.Empty:
            pass




def main():
    selectorThread = threading.Thread(target=selectorThreadFn, args=(NEW_CONNECTIONS_QUEUE, PROCESSING_QUEUE, DROP_CONNECTIONS_QUEUE), daemon=True)
    consumerThread = threading.Thread(target=consumerThreadFn, args=(PROCESSING_QUEUE, DROP_CONNECTIONS_QUEUE), daemon=True)
    threading.Thread(target=consumerThreadFn, args=(PROCESSING_QUEUE, DROP_CONNECTIONS_QUEUE), daemon=True).start()
    threading.Thread(target=consumerThreadFn, args=(PROCESSING_QUEUE, DROP_CONNECTIONS_QUEUE), daemon=True).start()

    selectorThread.start()
    consumerThread.start()
    serverThreadFn(NEW_CONNECTIONS_QUEUE)

if __name__ == "__main__":
    sys.exit(main())