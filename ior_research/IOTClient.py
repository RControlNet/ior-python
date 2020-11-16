import threading
import time
import json
import socket
import os
import logging


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
        logging.basicConfig(format=f'%(asctime)s - {token}-{code} %(message)s', level=logging.INFO)

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
        self.closed = False
        self.__s = None

        logging.info("*" * 80)
        logging.info("Using Beta - Version: %s" % self.version())
        logging.info("Server Configuration IP: %s" % (self.__server))
        logging.info("User Token %s" % self.__token)
        logging.info("From Code: %d    To Code: %d" % (self.__code, self.__to))
        logging.info("Time Delay(in Seconds): %d" % self.__time_delay)
        logging.info("Tunneling Enabled: " + str(self.isTunneled))
        logging.info("*" * 80)

        if not os.path.exists('./logs') and save_logs == True:
            os.mkdir('./logs')

        if(not self.reconnect()):
            raise Exception("Could not connect to Server at %s:%d-%d"%(self.__server,self.__httpPort,self.__port))
        self.setName("Reader-%s-%d"%(self.__token,self.__to))
        if not self.isTunneled:
            self.heartBeat = threading.Thread(target=IOTClient.__sendThread,args=(self,))
            self.heartBeat.setName("Heartbeat-%s-%d"%(self.__token,self.__code))
            self.heartBeat.start()



    @staticmethod
    def createRevertedClients(token,code,to,server="localhost",httpPort=8080,tcpPort=8000):
        client1 = IOTClient(token=token, debug=True, code=code, to=to, server=server, httpPort=httpPort,
                            tcpPort=tcpPort)
        client2 = IOTClient(token=token, debug=True, code=to, to=code, server=server, httpPort=httpPort,
                            tcpPort=tcpPort)

        return (client1,client2)
    @staticmethod
    def version():
        return "v0.3.7"

    def getSocket(self):
        if self.connected:
            return self.__s

    def reconnect(self):
        import requests
        r = requests.post('http://%s:%d/subscribe?uuid=%s&from=%d&to=%d' % (self.__server,self.__httpPort, self.__token, self.__code,self.__to))
        if r.status_code == 404:
            logging.info("Request Failed")
            return False;
        if r.status_code == 409:
            raise Exception("Conflict while connecting, may another device is pre connected to the server")
        if r.status_code != 201:
            raise Exception("Invalid Credentials")

        logging.info("Request Successfully made to Server")
        s = r.content
        logging.info(s)

        if(self.__s is not None):
            self.__s.close()
            self.__s = None

        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((self.__server, self.__port))
        self.__s.sendall(s);

        self.file = self.__s.makefile('rw')
        logging.info("Connected to Socket Server")

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
            except  AttributeError:
                if( self.closed):
                    logging.warning("Client already closed, Skipping update")
                    break;
            except ConnectionAbortedError as cae:
                self.connected = False
                logging.error("Connection Aborted",exc_info=True)
            finally:
                self.__lock.release()
            time.sleep(self.__time_delay)

    def set_on_receive(self,fn):
        self.on_receive = fn

    def __send(self,msg):
        if(self.connected == False):
            logging.error("Server not connected Skipping")
            return False
        try:
            data = json.dumps(msg)
            self.__lock.acquire()
            self.__s.send(data.encode() + b'\r\n')
        except ConnectionAbortedError as cae:
            self.connected = False
            logging.error(cae)
        finally:
            self.__lock.release()


    def sendMessage(self,message,metadata = None,status = None):
        msg = dict()
        msg["message"] = message
        if(status is not None):
            msg["status"] = status

        if metadata is not None:
            msg["syncData"] = metadata

        self.__send(msg)

    def close(self):
        self.connected = False
        self.closed = True

        self.__s.close()
        self.file.close()

        logging.info("Socket Closed")
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
        logging.info("Starting Thread")
        while not self.closed:
            if not self.connected:
                time.sleep(1)
                continue
            try:
                msg = self.readData()
                if msg is not None:
                    try:
                        self.on_receive(msg)
                    except Exception as ex:
                        logging.info("Error Occured while invoking Receive Function")
                        logging.info(ex)
            except socket.timeout:
                logging.info("socket timeout")
            except Exception as cae:
                self.connected = False
                logging.error("Error Occured!!!")
                logging.error(cae)
                break;
            time.sleep(0.01)
        logging.info("Thread Terminated")

class IOTClientWrapper(threading.Thread):
    def __init__(self,token,code,to,config: dict = None):
        threading.Thread.__init__(self)
        self.config = {
            "server": "localhost",
            "httpPort": 8080,
            "tcpPort": 8000,
            "token": token,
            "code": code,
            "to": to
        }
        if config is not None:
            for key,value in config.items():
                self.config[key] = value

        self.closed = False
        self.set_on_receive(None)
        self.client = self.recreateClient()

    def set_on_receive(self,fn):
        self.fn = fn

    def terminate(self):
        self.closed = True
        if self.client is not None:
            self.client.close()

    def sendMessage(self,**data):
        try:
            return self.client.sendMessage(**data)
        except Exception:
            return False

    def recreateClient(self):
        return IOTClient(**self.config)

    def run(self):
        while not self.closed:
            try:
                if self.client is None:
                    self.client = self.recreateClient()
                self.client.set_on_receive(self.fn)
                self.client.start()
                self.client.join()
                self.client.close()
                print("Watcher Thread Closed")
                del self.client
                self.client = None
            except Exception:
                logging.error("Watcher Error: ",exc_info=True)


def on_receive(x):
    global counter
    print("Received",x)

if __name__ == "__main__":
    config = {
        "server": "localhost",
        "httpPort": 5001,
        "tcpPort": 8000
    }
    token = "5a5a83c3-2588-42fb-84bd-fa3129a2ac45"
    code = 1234
    to = 789

    client1 = IOTClientWrapper(token,code,to,config=config)
    client2 = IOTClientWrapper(token,to,code,config = config);
    client2.set_on_receive(on_receive)

    client1.start()
    client2.start()

    while True:
        print("Sending Message")
        client1.sendMessage(message = "Hello from Client")
        time.sleep(1)

    print()
    print(counter)
    time.sleep(5000)

    client1.join()
    client2.join()

    client1.close()
    client2.close()
