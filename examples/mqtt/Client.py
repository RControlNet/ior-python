from ior_research.mqtt import Communicator
import time
from paho.mqtt.client import MQTTMessage

client = Communicator("default", 5457)
client.connect("localhost")

def on_message(msg: MQTTMessage):
    print(msg.payload)

client.setOnReceive(on_message)

while True:
    time.sleep(2)