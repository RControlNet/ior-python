import pygame
import time
import os
import sys

from cndi.events import EventHandler
from cndi.initializers import AppInitilizer

from ior_research.drone.messagetypes import MANUAL_CONTROL, SYNCKEY_THROTTLE, SYNCKEY_PITCH, SYNCKEY_ROLL, SYNCKEY_YAW
from ior_research.utils.consts.envs import RCONTROLNET_ENV, RCONTOLNET_PROFILE
import json
if RCONTOLNET_PROFILE not in os.environ:
    os.environ[RCONTOLNET_PROFILE] = "sender"

from cndi.annotations import Autowired, Bean

import ior_research.bean_definations
from ior_research.utils.initializers import Initializer

@Bean()
def getEventHandler() -> EventHandler:
    eventHandler = EventHandler()
    eventHandler.start()

    return eventHandler

def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print("Received",x)

initializer = None

MIN_THROTTLE = 1100
MAX_THROTTLE = 1700

def start():

    sys.path.append("../../")  # Append Parent folder path to System Environment Path

    @Autowired()
    def setInitlializer(i: Initializer):
        global initializer
        initializer = i

    app_initializer = AppInitilizer()
    app_initializer.run()

    config = {
        "server": "localhost",
        "httpPort": 5001,
        "tcpPort": 16456,
    }

    clients = initializer.initializeIOTWrapper(**config);
    # Instanciate IOTClientWrapper Object,
    client1 = clients[0]

    # Set on receive function, so that if a message is received this function should be called to execute some task
    client1.set_on_receive(on_receive)

    client1.start()  # Start first client
    time.sleep(5)

    pygame.display.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    assert joysticks.__len__() > 0 , "No Joystick found"
    x = joysticks[0]
    x.init()

    values = [0 for _ in range(x.get_numaxes())]

    BASE_THROTTLE = MIN_THROTTLE
    while True:
        pygame.event.pump()
        left_yaw = x.get_button(3)
        right_yaw = x.get_button(1)

        values[0] = 1500
        if left_yaw == 1:
            values[0] = 1450
        if right_yaw == 1:
            values[0] = 1550

        for i in range(1,x.get_numaxes()):
            values[i] = x.get_axis(i)
            if i == 1:
                if abs(values[i]) > 0.80:
                    up = x.get_button(4)
                    down = x.get_button(6)

                    if up == 1:
                        BASE_THROTTLE = min(MAX_THROTTLE, BASE_THROTTLE + 50)
                    if down == 1:
                        BASE_THROTTLE = max(MIN_THROTTLE, BASE_THROTTLE - 50)
                values[i] = BASE_THROTTLE + (values[i] * -100)
            else:
                values[i] = 1500 + (values[i] * 100)

            values[i] = int(values[i])


        yaw = values[0]
        throttle = values[1]
        pitch = values[4]
        roll = values[3]

        client1.sendMessage(message=MANUAL_CONTROL, metadata={
            SYNCKEY_THROTTLE: throttle,
            SYNCKEY_PITCH: pitch,
            SYNCKEY_ROLL: roll,
            SYNCKEY_YAW: yaw
        })

        # print(yaw, throttle, pitch, roll)
        time.sleep(0.05)

if __name__ == "__main__":
    start()