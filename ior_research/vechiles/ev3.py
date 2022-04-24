from ior_research.vechiles import IORVechile
from paho.mqtt.client import Client

class EV3Tank(IORVechile):
    def onConnect(self):
        pass
    def onMessage(self):
        pass

    def initialise(self):
        self.mqttClient: Client = self.configuration['mqtt']

    def move(self, speed):
        left_speed = speed
        right_speed = speed

        self.mqttClient.publish("ev3dev.motor.left.speed", str(left_speed))
        self.mqttClient.publish("ev3dev.motor.right.speed", str(right_speed))

    def steer(self, value, speed):
        value = min(100, value)
        value = max(-100, value)

        value /= 100

        if value != 0:
            left_speed = int(-value * speed)
            right_speed = int(value * speed)
        else:
            left_speed = speed
            right_speed = speed

        self.mqttClient.publish("ev3dev.motor.left.speed", str(left_speed))
        self.mqttClient.publish("ev3dev.motor.right.speed", str(right_speed))