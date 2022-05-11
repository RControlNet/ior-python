import pygame
import time
import os
import sys

from cndi.initializers import AppInitilizer

from ior_research.utils.consts.envs import RCONTROLNET_ENV, RCONTOLNET_PROFILE
import json
if RCONTOLNET_PROFILE not in os.environ:
    os.environ[RCONTOLNET_PROFILE] = "sender"

from cndi.annotations import Autowired

import ior_research.bean_definations
from ior_research.utils.initializers import Initializer

def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print("Received",x['message'])

initializer = None

MIN_THROTTLE = 1100
MAX_THROTTLE = 1700

def start():
    pygame.display.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    assert joysticks.__len__() > 0 , "No Joystick found"
    x = joysticks[0]
    x.init()

    values = [0 for _ in range(x.get_numaxes())]

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
        "tcpPort": 8000,
    }

    clients = initializer.initializeIOTWrapper(**config);
    # Instanciate IOTClientWrapper Object,
    client1 = clients[0]

    # Set on receive function, so that if a message is received this function should be called to execute some task
    client1.set_on_receive(on_receive)

    client1.start()  # Start first client
    time.sleep(5)


    BASE_THROTTLE = MIN_THROTTLE
    while True:
        pygame.event.pump()
        for i in range(x.get_numbuttons()):
            print(x.get_button(i), end = " ")
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

        print(values)
        client1.sendMessage(message=json.dumps({
            "throttle": throttle,
            "pitch": int(pitch),
            "roll": int(roll),
            "yaw": int(yaw)
        }))

        # print(yaw, throttle, pitch, roll)
        time.sleep(0.2)

if __name__ == "__main__":
    start()