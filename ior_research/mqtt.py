import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage
import json
from ior_research import SocketMessage

class Communicator:
    """
    Control Net Communicator for MQTT Protocol, it manages Protocol conversion from ControlNet Protocol to MQTT and vice versa
    """
    def __init__(self,  token: str, deviceCode: str):
        """
        token: unique identified string aka (api key)
        deviceCode: Any alpha numeric string
        """
        self.token = token
        self.deviceCode = deviceCode
        self.client = mqtt.Client()
        self.connected = None
        self.onReceive = None

    def connect(self, server="localhost"):
        """
        Connects to mqtt server on port 1883.
        """
        self.client.connect(server, 1883)
        self.client.on_connect = self.__onConnect
        self.client.loop_start()

    def __onConnect(self, client, userdata, flags, rc):
        """
        OnConnect method automatically subscribes to default topics for ControlNet and calls connected method if set by user
        client: MQTTClient object
        """
        #client.subscribe("$SYS/#")
        self.client.subscribe(self.token)
        self.client.subscribe("%s/%s"%(self.token,self.deviceCode))
        if self.connected is not None:
            self.connected(client, userdata, flags, rc)

    def __onReceive(self, client, userdata, msg):
        """
        OnReceive method invokes whenever a client message is received
        """
        if self.onReceive is not None:
            self.onReceive(msg)

    def setOnConnect(self, onConnect):
        """
        setOnConnect method sets a onConnect method.
        onConnect: takes a function
        """
        self.connected = onConnect

    def setOnReceive(self, onReceive):
        """
        setOnReceive method sets a onReceive method.
        onReceive: takes a function
        """
        self.onReceive = onReceive
        self.client.on_message = self.__onReceive

    def sendObject(self, obj, to=None):
        """
        publish message to MQTT Broker
        sm: SocketMessage object
        to: optional parameter, specifies a target client
        """
        payload = json.dumps(obj, cls=SocketMessage)
        self.sendMessage(sm=payload, to=to)
    def sendMessage(self,sm,to=None):
        """
        publish message to MQTT Broker
        sm: Message String
        to: optional parameter, specifies a target client
        """
        path = self.token
        if(to != None):
            path += "/" + to
        self.client.publish(path, sm)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(msg:MQTTMessage, payload: dict):
    print(msg.topic,payload)

def createClient(token,code,server="localhost"):
    client = Communicator(token,code)
    client.connect(server)
    return client

def createReverseClients(token, code1, code2, server="localhost"):
    """
    Create a pair of communicator clients given by common token and unique device codes
    token: A Alphanumeric String aka (api key)
    code1: device 1 code
    code2: device 2 code
    server: optional parameter, defines MQTT Broker ip address
    """
    client1 = Communicator(token, code1)
    client1.connect(server)

    client2 = Communicator(token, code2)
    client2.connect(server)

    return client1, client2

if __name__ == "__main__":
    import time
    code1,code2 = "1234","5678"

    # Creates a Pair of Communicator Clients
    client1,client2 = createReverseClients("default",code1,code2)

    # Set onConnect method
    client1.setOnConnect(on_connect)
    client2.setOnConnect(on_connect)

    # Set onReceive method
    client1.setOnReceive(on_message)
    client2.setOnReceive(on_message)

    # Let the clients initialise for 2 sec
    time.sleep(2)

    while True:
        # Sends message specific to client with code2
        client1.sendObject(SocketMessage("From 1"), to=code2)
        time.sleep(1)
        # Sends message specific to client with code1
        client2.sendObject(SocketMessage("From 2"), to=code1)

