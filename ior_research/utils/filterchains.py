from ior_research.utils.text import SocketMessage
from ior_research.utils.consts import DroneOperations

class MessageFilterChain:
    def doFilter(self,message):
        pass;

class RControlNetMessageFilter(MessageFilterChain):
    def __init__(self, initializer):
        self.initializer = initializer

    def doFilter(self,message):
        message = SocketMessage(**message)
        print("RControlNet Filter", message.__dict__)

        if message.message == DroneOperations.START_STREAMER.name:
            if self.initializer.transmitter is None:
                self.initializer.initializeVideoTransmitter()
            elif self.initializer.transmitter.checkBrowserAlive():
                self.initializer.transmitter.close()
            self.initializer.transmitter.openBrowserAndHitLink()
            return None

        if message.message == DroneOperations.STOP_STREAMER.name:
            if self.initializer.transmitter is not None and self.initializer.transmitter.checkBrowserAlive():
                self.initializer.transmitter.close()
            return None
        return message