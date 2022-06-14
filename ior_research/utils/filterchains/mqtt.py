import logging

from cndi.annotations import Autowired

from ior_research.utils.filterchains import MessageFilterChain
from ior_research.utils.text import socketMessageSchema


class MQTTPublisher(MessageFilterChain):
    logger = logging.getLogger(f"{MessageFilterChain.__module__}.{MessageFilterChain.__name__}")

    def initializeMqttClient(self, server, port, defaultTopic):
        from paho.mqtt.client import Client
        def on_connect(client: Client, userdata, flags, rc):
            print("Connected with result code " + str(rc))
            client.subscribe(defaultTopic)

        def on_message(client: Client, userdata, msg):
            print(msg.topic + " " + str(msg.payload))

        @Autowired()
        def setMqttClient(client: Client):
            client.on_message = on_message
            client.on_connect = on_connect

            client.connect(server, port)
            client.loop_start()
            self.client = client

    def initialise(self):
        self.client = None
        self.server = self.getOrElseRaiseException("server")
        self.port = int(self.getOrElseRaiseException("port"))
        self.defaultTopic = self.getOrElseRaiseException("defaultTopic", "rcn.robot.controller")

        self.initializeMqttClient(self.server, self.port, self.defaultTopic)


    def doFilter(self,message):
        operatedMessage = socketMessageSchema.dumps(message)
        try:
            if self.client is not None:
                self.client.publish(self.defaultTopic, operatedMessage)
            else:
                self.logger.warning("MQTT Client not Initialised properly")
        except Exception as e:
            self.logger.error("Error occured while publishing the message" + e)
        return message