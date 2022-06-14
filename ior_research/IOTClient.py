import sys, os

sys.path.append(os.getcwd())

import threading
import time
import socket
import json
import os
import logging, base64
from ior_research.utils.aes import ControlNetAES
from ior_research.utils.serialization import JSONSerializer,JSONDeserializer
import asyncio

logging.basicConfig(format=f'%(asctime)s - %(name)s %(message)s', level=logging.INFO)

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
        self.serializer = JSONSerializer()
        self.deserializer = JSONDeserializer()
        self.lastMessageRead = time.time()
        self.setOnConnect(onConnect)

        if socketServer is None:
            self.__tunnelServer = self.__server
        else:
            self.__tunnelServer = socketServer
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.logger.info("*" * 80)
        self.logger.info("Using Beta - Version: %s" % self.version())
        self.logger.info("Server Configuration IP: %s" % (self.__server))
        self.logger.info("User Token %s" % self.__token)
        self.logger.info("From Code: %d" % (self.__code))
        self.logger.info("Time Delay(in Seconds): %d" % self.__time_delay)
        self.logger.info("Tunneling Enabled: " + str(self.isTunneled))
        self.logger.info("*" * 80)

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
        logging.debug("Response Status Code: %d" % r.status_code)
        if r.status_code == 404:
            self.logger.info("Request Failed")
            return False;
        if r.status_code == 409:
            raise Exception("Conflict while connecting, may another device is pre connected to the server")
        if r.status_code != 201:
            raise Exception("Invalid Credentials")

        self.logger.info("Request Successfully made to Server")
        s = r.content
        self.logger.info(s)

        if(self.__s is not None):
            self.__s.close()
            self.__s = None

        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((self.__tunnelServer, self.__port))
        self.__s.sendall(s);

        self.aes = ControlNetAES(self.__key)

        self.file = self.__s.makefile('rw')
        self.logger.info("Connected to Socket Server")

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
                self.logger.debug("Heartbeat message successfully send")
            except  AttributeError:
                if( self.closed):
                    self.logger.warning("Client already closed, Skipping update")
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

            data = self.serializer.serialize(msg)
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

        self.logger.info("Socket Closed")
        if self.__on_close != None:
            self.__on_close()

    def readData(self):
        """
        Read data sended by server
        """

        dataString = self.file.readline()
        self.lastMessageRead = time.time()

        if(dataString == ""):
            return None

        try:
            dataString = self.aes.decrypt(dataString)
            data = self.deserializer.deserialize(dataString)
            if(data['message'] == "HEARTBEAT"):
                return None
        except Exception as ex:
            self.logger.error(f"Error occured while receiving data: {ex}")
            data = dict(message = dataString)

        self.sendMessage("ack")
        return data

    def run(self):
        self.logger.info("Starting Thread")
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
                        self.logger.error("Error Occured while invoking Receive Function")
                        self.logger.error(ex)
            except socket.timeout:
                self.logger.info("socket timeout")
            except Exception as cae:
                self.connected = False
                self.logger.error("Error Occured!!!")
                self.logger.error(cae)
                break;
            time.sleep(0.01)
        self.logger.info("Thread Terminated")

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

        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        if config is not None:
            for key,value in config.items():
                self.config[key] = value

        if "file" in self.config:
            with open(self.config['file'], "r") as file:
                data = base64.b64decode(file.read()).decode()
                data = json.loads(data)
                self.logger.info(f"File Data: {data}")
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
                # while not self.client.closed:
                #     time.sleep(0.5)
                #     timeDiff = time.time() - self.client.lastMessageRead
                #     if timeDiff > 0.5:
                #         print("Timeout: ", timeDiff)
                self.client.close()
                print("Watcher Thread Closed")
                del self.client
                self.client = None
            except Exception:
                logging.error("Watcher Error: ",exc_info=True)