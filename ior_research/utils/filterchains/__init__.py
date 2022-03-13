import json

from ior_research.utils.consts import DroneOperations
from ior_research.utils.text import SocketMessage
import logging


class MessageFilterChain:
    def __init__(self, initializer, configuration=None):
        self.initializer = initializer
        self.configuration = configuration
        self.initialise()

    def initialise(self):
        pass
    def doFilter(self,message):
        pass;

class LogMessage(MessageFilterChain):
    def initialise(self):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def doFilter(self,message):
        operatedMessage = message
        if isinstance(message, SocketMessage):
            operatedMessage = message.__dict__

        self.logger.info(f"Incomming Message {operatedMessage}")

        return message

class AirSimConnectorFilter(MessageFilterChain):
    def initialise(self):
        import airsim
        self.copter = airsim.MultirotorClient()
        self.copter.enableApiControl(True)
        self.copter.reset()
        print(self.configuration)

    def doFilter(self,message):
        # if "message" not in message:
        #     return message

        data = json.loads(message.message)
        self.copter.moveByVelocityAsync(data['roll'] * 5, data['pitch'] * 5, data['throttle'] * -1,duration=0.2)
        return message

class RControlNetMessageFilter(MessageFilterChain):
    def doFilter(self,message):
        message = SocketMessage(**message)
        # if message.message == DroneOperations.START_STREAMER.name:
        #     if self.initializer.transmitter is None:
        #         self.initializer.initializeVideoTransmitter()
        #     elif self.initializer.transmitter.checkBrowserAlive():
        #         self.initializer.transmitter.close()
        #     self.initializer.transmitter.openBrowserAndHitLink()
        #
        #
        # if message.message == DroneOperations.STOP_STREAMER.name:
        #     if self.initializer.transmitter is not None and self.initializer.transmitter.checkBrowserAlive():
        #         self.initializer.transmitter.close()

        return message