from ior_research.mqtt import Communicator
import time
from paho.mqtt.client import MQTTMessage
from ev3dev.ev3 import *

client = Communicator("default", 5457)
client.connect("localhost")


motorB = LargeMotor('outB')
motorC = LargeMotor('outC')

speed = 500

def on_message(msg: MQTTMessage):
    message = msg.payload.decode()
    command = message[0]
    state = int(message[2])

    print(command, state)

    global speed

    if "U" == command:
        if state == 1:
            motorB.run_forever(speed_sp=speed)
            motorC.run_forever(speed_sp=speed)
        else:
            motorB.stop()
            motorC.stop()

    if "D" == command:
        if state == 1:
            motorB.run_forever(speed_sp=-speed)
            motorC.run_forever(speed_sp=-speed)
        else:
            motorB.stop()
            motorC.stop()

    if "R" == command:
        if state == 1:
            motorB.run_forever(speed_sp=speed)
            motorC.run_forever(speed_sp=-speed)
        else:
            motorB.stop()
            motorC.stop()

    if "L" == command:
        if state == 1:
            motorB.run_forever(speed_sp=-speed)
            motorC.run_forever(speed_sp=speed)
        else:
            motorB.stop()
            motorC.stop()

client.setOnReceive(on_message)

while True:
    time.sleep(2)