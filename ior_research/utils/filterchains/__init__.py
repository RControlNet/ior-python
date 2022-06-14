from ior_research.utils.consts import DroneOperations
import json

from ior_research.utils.text import socketMessageSchema


class MessageFilterChain:
    def __init__(self, initializer, configuration=None):
        self.initializer = initializer
        self.configuration = configuration
        self.initialise()
    def getOrElseRaiseException(self, configurationAttribute, defaultValue=None):
        if configurationAttribute not in self.configuration:
            if defaultValue is not None:
                return defaultValue
            raise KeyError(f"Key {configurationAttribute} not in RCN Filter Configuration")
        return self.configuration[configurationAttribute]
    def initialise(self):
        pass
    def doFilter(self,message):
        pass;

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
        message = socketMessageSchema.dump(message)
        return message