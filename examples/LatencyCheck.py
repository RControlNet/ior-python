import time, sys
import os

from ior_research.utils.consts.envs import RCONTROLNET_ENV

os.environ[RCONTROLNET_ENV] = "C:/Users/Asus/git/ior-python/config/iorConfigs.yml"
from cndi.annotations import Autowired, AppInitilizer

import ior_research.bean_definations
from ior_research.utils.initializers import Initializer


def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print("Received",time.time() - float(x['message']))

if __name__ == "__main__":
    sys.path.append("../") # Append Parent folder path to System Environment Path
    initializer = None
    @Autowired()
    def setInitlializer(i: Initializer):
        global initializer
        initializer = i

    app_initializer = AppInitilizer()
    app_initializer.run()

    # from ior_research.IOTClient import IOTClientWrapper # Import IOTClientWrapper
    # import argparse
    # # Build Config Object, you can supply various keyword argument to below dict object
    config = {
        "server": "192.168.46.241",
        "httpPort": 31520,
        "tcpPort": 31459,
    }





    token = "default" # Define and Assign Token, "default" is the default token value
    clients = initializer.initializeIOTWrapper(**config);
    # Instanciate IOTClientWrapper Object,
    client1 = clients[0]
    client2 = clients[1]

    # Set on receive function, so that if a message is received this function should be called to execute some task
    client2.set_on_receive(on_receive)
    client1.set_on_receive(on_receive)

    client1.start()     # Start first client
    client2.start()     # Start second client
    time.sleep(5)
    try:
        while True:
            # Send a message at a frequency of 1 Hz
            # print("Sending Message")
            client1.sendMessage(message = str(time.time()))
            time.sleep(0.1)
    finally:
        exit()

