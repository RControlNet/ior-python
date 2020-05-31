import threading
import time
import json
import socket
import os

class IOTClient(threading.Thread):
    """Class used to access IOR Server"""

    def __init__(self,code,token,to,time_delay = 3,debug=False,on_close = None,save_logs=False,server = "iorcloud.ml",httpPort = 8080,tcpPort = 8000,isTunneled = False):
        """
        :param code: Current Device code
        :param token: Subscription Key
        :param to: Receiver Device Code
        :param time_delay: Time Delay for a Heartbeat @Deprecated
        :param debug: See all the message in I/O stream on the CLI
        :param on_close: a function that has to be called when the connection is closed
        :param save_logs: Save Logs of all the messages
        """

        threading.Thread.__init__(self)
        self.__code = code
        self.__token = token
        self.__to = to
        self.__time_delay = time_delay
        self.__port = tcpPort
        self.__httpPort = httpPort

        self.debug = debug
        self.__on_close = on_close
        self.__save_logs = save_logs
        self.__lock = threading.Lock()
        self.__server = server
        self.isTunneled = isTunneled
        self.connected = False

        self._writeline("*" * 80)
        self._writeline("Using Beta - Version: %s" % self.version())
        self._writeline("Server Configuration IP: %s" % (self.__server))
        self._writeline("User Token %s" % self.__token)
        self._writeline("From Code: %d    To Code: %d" % (self.__code, self.__to))
        self._writeline("Time Delay(in Seconds): %d" % self.__time_delay)
        self._writeline("Tunneling Enabled: " + str(self.isTunneled))
        self._writeline("*" * 80)

        if not os.path.exists('./logs') and save_logs == True:
            os.mkdir('./logs')

        if(not self.reconnect()):
            raise Exception("Could not connect to Server at %s:%d-%d"%(self.__server,self.__httpPort,self.__port))
    @staticmethod
    def createRevertedClients():
        pass
    @staticmethod
    def version():
        return "v0.3.7"

    def getSocket(self):
        if self.connected:
            return self.__s

    def reconnect(self):
        import requests
        r = requests.post('http://%s:%d/subscribe/%s/%d/%d' % (self.__server,self.__httpPort, self.__token, self.__code,self.__to))
        if r.status_code == 404:
            self._writeline("Request Failed")
            return False;
        if r.status_code == 409:
            raise Exception("Conflict while connecting, may another device is pre connected to the server")
        if r.status_code != 201:
            raise Exception("Invalid Credentials")

        print("Request Successfully made to Server")
        s = r.content
        print(s)

        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((self.__server, self.__port))
        self.__s.sendall(s);

        self.file = self.__s.makefile('rw')
        self._writeline("Connected to Socket Server")

        if not self.isTunneled:
            self.heartBeat = threading.Thread(target=IOTClient.__sendThread,args=(self,))
            self.heartBeat.start()

        self.connected = True
        return True

    def __del__(self):
        self.close();

    def __sendThread(self):
        time.sleep(0.5)
        while True:
            try:
                self.__lock.acquire()
                self.getSocket().send(b"\n")
            finally:
                self.__lock.release()
            time.sleep(self.__time_delay)

    def set_on_receive(self,fn):
        self.on_receive = fn

    def _writeline(self,msg):
        if self.debug:
            print(msg)

    def __send(self,msg):
        try:
            data = json.dumps(msg)
            print(data)
            self.__lock.acquire()
            self.__s.send(data.encode() + b'\r\n')
        finally:
            self.__lock.release()


    def sendMessage(self,message,metadata = None):
        msg = dict()
        msg["message"] = message
        if metadata is not None:
            msg["syncData"] = metadata

        self.__send(msg)

    def close(self):
        self.connected = False

        self.__s.close()
        self.file.close()

        self._writeline("Socket Closed")
        if self.__on_close != None:
            self.__on_close()

    def readData(self):
        dataString = self.file.readline()
        if(dataString == ""):
            return None
        print("DataString: ",dataString)
        data = json.loads(dataString)
        self.sendMessage("ack");
        return data

    def run(self):
        self._writeline("Starting Thread")
        while self.connected:
            try:
                msg = self.readData()
                if msg is not None:
                    try:
                        self.on_receive(msg)
                    except Exception as ex:
                        self._writeline("Error Occured while invoking Receive Function")
                        self._writeline(ex)
            except socket.timeout:
                print("socket timeout")
            except Exception as cae:
                print("Error Occured!!!")
                print(cae)
                break;
            time.sleep(0.01)
        print("Thread Terminated")
        self.close()

token = "5a5a83c3-2588-42fb-84bd-fa3129a2ac45"
code = 1234
to = 789

counter = 0
def on_receive(x):
    global counter
    print(counter,"Received",x)
    counter += 1

if __name__ == "__main__":
    client1 = IOTClient(token=token,debug=True,code=code,to=to,server="192.168.46.3")
    client2 = IOTClient(token=token, debug=True, code=to, to=code, server="192.168.46.3")
    client1.start()
    client2.start()
    client2.set_on_receive(on_receive)
    for i in range(10):
        print(i)
        client1.sendMessage("Hello from Client")
        time.sleep(0.01)
    print()
    print(counter)
    time.sleep(5000)
    client1.close()
    client2.close()
