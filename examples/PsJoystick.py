import pygame
import time
import os
import sys

from ior_research.utils.consts.envs import RCONTROLNET_ENV
import json
if RCONTROLNET_ENV not in os.environ:
    os.environ[RCONTROLNET_ENV] = "C:/Users/Asus/git/ior-python/config/iorConfigsFrom.yml"
from cndi.annotations import Autowired, AppInitilizer

import ior_research.bean_definations
from ior_research.utils.initializers import Initializer

def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print("Received",x['message'])

initializer = None

def start():
    pygame.display.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    assert joysticks.__len__() > 0 , "No Joystick found"
    x = joysticks[0]
    x.init()

    values = [0 for _ in range(x.get_numaxes())]

    sys.path.append("../")  # Append Parent folder path to System Environment Path


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

    while True:
        pygame.event.pump()
        for i in range(x.get_numaxes()):
            values[i] = x.get_axis(i)

        yaw = values[0]
        throttle = values[1]
        pitch = values[4]
        roll = values[3]

        client1.sendMessage(message=json.dumps({
            "throttle": throttle,
            "pitch": pitch,
            "roll": roll,
            "yaw": yaw
        }))

        # print(yaw, throttle, pitch, roll)
        time.sleep(0.2)

if __name__ == "__main__":
    start()