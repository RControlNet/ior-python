import json

from cndi.annotations import Autowired

from ior_research.utils.filterchains import MessageFilterChain
from ior_research.utils.text import SocketMessage


class MQTTPublisher(MessageFilterChain):
    def getOrElseRaiseException(self, configurationAttribute, defaultValue=None):
        if configurationAttribute not in self.configuration:
            if defaultValue is not None:
                return defaultValue
            raise KeyError(f"Key {configurationAttribute} not in RCN Filter Configuration")
        return self.configuration[configurationAttribute]

    def initialise(self):
        self.server = self.getOrElseRaiseException("server")
        self.port = int(self.getOrElseRaiseException("port"))
        self.defaultTopic = self.getOrElseRaiseException("defaultTopic", "rcn.robot.controller")

        from paho.mqtt.client import Client
        def on_connect(client: Client, userdata, flags, rc):
            print("Connected with result code " + str(rc))
            client.subscribe(self.defaultTopic)

        def on_message(client: Client, userdata, msg):
            print(msg.topic + " " + str(msg.payload))

        @Autowired()
        def setMqttClient(client: Client):
            client.on_message = on_message
            client.on_connect = on_connect

            client.connect(self.server,self.port)
            client.loop_start()
            self.client = client
            print("Client Set", self.client)

    def doFilter(self,message):
        operatedMessage = message
        if isinstance(message, SocketMessage):
            operatedMessage = message.__dict__
        operatedMessage = json.dumps(operatedMessage)

        self.client.publish(self.defaultTopic, operatedMessage)

        return message