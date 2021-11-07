from ior_research.utils.text import SocketMessage
from ior_research.utils.consts import DroneOperations

class MessageFilterChain:
    def __init__(self, initializer):
        self.initializer = initializer

    def doFilter(self,message):
        pass;

class RControlNetMessageFilter(MessageFilterChain):
    def doFilter(self,message):
        print(message)
        message = SocketMessage(**message)
        if message.message == DroneOperations.START_STREAMER.name:
            if self.initializer.transmitter is None:
                self.initializer.initializeVideoTransmitter()
            elif self.initializer.transmitter.checkBrowserAlive():
                self.initializer.transmitter.close()
            self.initializer.transmitter.openBrowserAndHitLink()


        if message.message == DroneOperations.STOP_STREAMER.name:
            if self.initializer.transmitter is not None and self.initializer.transmitter.checkBrowserAlive():
                self.initializer.transmitter.close()

        return message