from builtins import super

from cndi.annotations import Autowired

from ior_research.utils.filterchains.mqtt import MQTTPublisher
from ior_research.utils.text import SocketMessage
from ior_research.vechiles.ev3 import EV3Tank


class VechileControllerFilterChain(MQTTPublisher):
    def initialise(self):
        super(VechileControllerFilterChain, self).initialise()
        from paho.mqtt.client import Client
        @Autowired()
        def setMqttClient(client: Client):
            self.vechile = EV3Tank(configuration={
                'mqtt': client
            })

    def doFilter(self,message: SocketMessage):
        if message.syncData is None:
            return message

        speed = int(message.syncData['speed'])
        steer = int(message.syncData['steer'])

        self.vechile.steer(steer, speed)

        return message