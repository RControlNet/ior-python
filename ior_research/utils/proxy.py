import socket
import threading
import time
import json
import logging

class ProxyServer(threading.Thread):
    def __init__(self, server, callback):
        threading.Thread.__init__(self)
        self.server = server[0]
        self.port = server[1]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.server, self.port))
        self.callback = callback
        self.client = None

    def run(self) -> None:
        self.socket.listen(1)
        print("Listening for Clients")
        while True:
            socket_, addr = self.socket.accept()
            print("Client Connected ", addr)
            self.client = ProxyClient()
            self.client.connect(clientSocket=socket_, callback=self.callback)
            self.client.start()
            self.client.join()


class ProxyClient(threading.Thread):
    def __init__(self, ):
        threading.Thread.__init__(self)
        self.server = self.port = None
        self.file = self.callback = self.socket = None

    def connect(self, callback, clientSocket=None, server=None):
        if clientSocket is None:
            self.server = server[0]
            self.port = server[1]
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server, self.port))
        else:
            self.socket = clientSocket
        self.file = self.socket.makefile('rb')
        self.callback = callback

    def sendData(self, msg):
        self.socket.sendall(msg + b'\r\n')

    def run(self) -> None:
        while True:
            data = self.file.readline()
            data = json.loads(data.decode()[:-2])
            try:
                self.callback(data)
            except Exception as ex:
                logging.info("Exception occured while trying to callback on ProxyClient", ex)



if __name__ == "__main__":
    server = ProxyServer(server=('', 54753), callback=lambda x: print(x))
    server.start()
    server.join()
    
    time.sleep(0.5)

    client = ProxyClient()
    client.connect(server=("localhost", 54753), callback=lambda x: print(x))
    client.start()

    while True:
        client.sendData(b'Hello World')
        time.sleep(1)
