import sys, os

sys.path.append(os.getcwd())

import threading
import time
import json
import socket
import os
import logging, base64
from ior_research.utils.aes import ControlNetAES

class IOTClient(threading.Thread):
    """Class used to access IOR Server"""

    def __init__(self,code,token,server,time_delay = 3,key=None,debug=False,on_close = None,save_logs=False,onConnect=None, socketServer = None,httpPort = 8080,tcpPort = 8000,isTunneled = False, useSSL=False):
        """
        :param code: Current Device code
        :param token: Subscription Key
        :param key: AES Encryption key, which is already defined in connections.json frile
        :param time_delay: Time Delay for a Heartbeat @Deprecated
        :param debug: See all the message in I/O stream on the CLI
        :param on_close: a function that has to be called when the connection is closed
        :param save_logs: Save Logs of all the messages, default value is False
        :param server: address of the server
        :param socket_server: (optional) only use when you have different address of ior-backend and socket-server
        :param httpPort: port to register a device on server, default value is 8080
        :param tcpPort: port on which TCP Sockets will communicate to, default value is 8000
        :param useSSL: (optional) specifies if client should communicate in http or https, default value is False
        """

        threading.Thread.__init__(self)
        #logging.basicConfig(format=f'%(asctime)s - {token}-{code} %(message)s', level=logging.INFO)

        self.__code = code
        self.__token = token
        self.__time_delay = time_delay
        self.__port = tcpPort
        self.__httpPort = httpPort
        self.__key = key
        self.useSSL = useSSL

        self.debug = debug
        self.__on_close = on_close
        self.__save_logs = save_logs
        self.__lock = threading.Lock()
        self.__server = server
        self.isTunneled = isTunneled
        self.connected = False
        self.closed = False
        self.__s = None
        self.setOnConnect(onConnect)

        if socketServer is None:
            self.__tunnelServer = self.__server
        else:
            self.__tunnelServer = socketServer

        logging.info("*" * 80)
        logging.info("Using Beta - Version: %s" % self.version())
        logging.info("Server Configuration IP: %s" % (self.__server))
        logging.info("User Token %s" % self.__token)
        logging.info("From Code: %d" % (self.__code))
        logging.info("Time Delay(in Seconds): %d" % self.__time_delay)
        logging.info("Tunneling Enabled: " + str(self.isTunneled))
        logging.info("*" * 80)

        if not os.path.exists('./logs') and save_logs == True:
            os.mkdir('./logs')

        if(not self.reconnect()):
            raise Exception("Could not connect to Server at %s:%d-%d"%(self.__server,self.__httpPort,self.__port))
        self.setName("Reader-%s-%d"%(self.__token, self.__code))
        if not self.isTunneled:
            self.heartBeat = threading.Thread(target=IOTClient.__sendThread,args=(self,))
            self.heartBeat.setName("Heartbeat-%s-%d"%(self.__token,self.__code))
            self.heartBeat.start()



    @staticmethod
    def createRevertedClients(token,code,to,server="localhost",httpPort=8080,tcpPort=8000):
        client1 = IOTClient(token=token, debug=True, code=code, server=server, httpPort=httpPort,
                            tcpPort=tcpPort)
        client2 = IOTClient(token=token, debug=True, code=to, server=server, httpPort=httpPort,
                            tcpPort=tcpPort)

        return (client1,client2)

    def setOnConnect(self, on_connect):
        self.onConnect = on_connect
    @staticmethod
    def version():
        return "v0.3.7"

    def getSocket(self):
        if self.connected:
            return self.__s

    def reconnect(self):
        """
        Reconnects IOT Client to server
        """
        import requests
        if self.useSSL:
            r = requests.post('https://%s:%s/tunnel/subscribe?uuid=%s&from=%d' % (self.__server,self.__httpPort ,self.__token, self.__code), verify=False)
        else:
            r = requests.post(
                'http://%s:%s/tunnel/subscribe?uuid=%s&from=%d' % (self.__server,self.__httpPort, self.__token, self.__code))
        print(r.status_code)
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
        self.__s.connect((self.__tunnelServer, self.__port))
        self.__s.sendall(s);

        self.aes = ControlNetAES(self.__key)

        self.file = self.__s.makefile('rw')
        logging.info("Connected to Socket Server")

        self.connected = True
        if(self.onConnect is not None):
            self.onConnect()
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
        """
        Sends Message to control net tunnel server
        """
        if(self.connected == False):
            logging.error("Server not connected Skipping")
            return False
        try:
            data = json.dumps(msg)
            data = self.aes.encrypt(data)

            self.__lock.acquire()
            self.__s.send(data + b'\r\n')
        except ConnectionAbortedError as cae:
            self.connected = False
            logging.error(cae)
        finally:
            self.__lock.release()


    def sendMessage(self,message,metadata = None,status = None):
        """
        Sends message to server, also constructs message to server acceptable format
        message: alpha numeric string
        metadata: optional object, that specificies additional data on transfer
        status: optional field, it specifies message type
        """
        msg = dict()
        msg["message"] = message
        if(status is not None):
            msg["status"] = status

        if metadata is not None:
            msg["syncData"] = metadata

        self.__send(msg)

    def close(self):
        """
        Closes the client and terminates the running Thread
        """
        self.connected = False
        self.closed = True

        self.__s.close()
        self.file.close()

        logging.info("Socket Closed")
        if self.__on_close != None:
            self.__on_close()

    def readData(self):
        """
        Read data sended by server
        """
        dataString = self.file.readline()
        if(dataString == ""):
            return None
        dataString = self.aes.decrypt(dataString)
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
    """
    IOTClientWrapper is class, which wrapes IOTClient clients. It manages connection status to the server and handles IOTClient receiving messages
    """
    def __init__(self,token,config: dict = None,code = None):
        """
        Constructs object of IOTClientWrapper Class,
        """
        threading.Thread.__init__(self)
        self.config = {
            "server": "localhost",
            "httpPort": 8080,
            "tcpPort": 8000,
            "token": token,
            "code": code,
        }

        if config is not None:
            for key,value in config.items():
                self.config[key] = value

        if "file" in self.config:
            with open(self.config['file'], "r") as file:
                data = base64.b64decode(file.read()).decode()
                data = json.loads(data)
                print(data)
                self.config['code'] = data['deviceCode']
                self.config['key'] = data['key']
            self.config.pop('file')


        self.closed = False
        self.set_on_receive(None)
        self.setOnConnect(None)
        self.client = None


    def setOnConnect(self, onConnect):
        self.onConnect = onConnect

    def set_on_receive(self,fn):
        """
        sets on receive function which is called everytime a message is received
        fn: function to be called when a message is received
        """
        self.fn = fn

    def terminate(self):
        """
        Terminates IOT Client connection to the server and closes the client
        """
        self.closed = True
        if self.client is not None:
            self.client.close()

    def sendMessage(self,**data):
        """
        Send message to server
        :param **data: a dict object, acceptable key-values are
            message: main message \n
            status: (optional) status of the message \n
            metadata: (optional) metadata of the message, if any
        """
        try:
            return self.client.sendMessage(**data)
        except Exception:
            return False

    def recreateClient(self):
        """
        Recreates IOT Client from config
        """
        client = IOTClient(**self.config, onConnect=self.onConnect)
        return client

    def run(self):
        self.client = self.recreateClient()
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