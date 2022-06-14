import os
import sys

from cndi.binders.message import Input
from cndi.env import loadEnvFromFile
from cndi.initializers import AppInitilizer

from ior_research.IOTClient import IOTClientWrapper
from ior_research.utils.consts.envs import RCONTROLNET_ENV, RCONTOLNET_PROFILE
import json

if RCONTOLNET_PROFILE not in os.environ:
    os.environ[RCONTOLNET_PROFILE] = "receiver"

from examples.utils.client import connect, setMode, desiredAltitude, moveWithVelocity, increseAltitude, setHeading
from cndi.annotations import Autowired
from ior_research.utils.initializers import Initializer

# import smbus2
#
# ARDUINO_ADDRESS = 0x08
#
# bus = smbus2.SMBus(1);
#
# def write(index, value):
#     bus.write_i2c_block_data(ARDUINO_ADDRESS, index, [(value >> 8) & 0xFF, value & 0xFF])
    
def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print("Received",x)
    # message = json.loads(x['message'])
    # try:
    #     throttle = int(1370 + (float(message['throttle']) * -250)) + 20
    #     roll = int(1500 + (float(message['roll']) * 100)) + 20
    #     pitch = int(1500 + (float(message['pitch']) * 100)) + 20
    #     yaw = int(1500 + (float(message['yaw']) * 100)) + 20
    #     if throttle < 1100:
    #         throttle = 1100;
    #
    #     print(roll,pitch,throttle,yaw)
    #     write(0, roll)
    #     write(1, pitch)
    #     #write(2, throttle)
    #     write(3, yaw)
    # except Exception as e:
    #     print(e)

STORE = dict(initializer=None,
             iorClient=None)

vehicle = None
DEFAULT_CHANNEL = "mqtt-to-ior-channel"

@Input(DEFAULT_CHANNEL)
def handleInputMessage(message):
    client: IOTClientWrapper = STORE['iorClient']
    if client is not None:
        message = json.loads(message.payload.decode())
        data = dict(
            message=message['message'],
            metadata= message['syncData'] if 'syncData' in message else dict()
        )
        client.sendMessage(**data)

def start():
    global  vehicle

    sys.path.append("../../")  # Append Parent folder path to System Environment Path

    @Autowired()
    def setInitlializer(i: Initializer):
        global initializer
        STORE['initializer'] = i
        initializer = i

    loadEnvFromFile("../../resources/receiver.yml")
    app_initializer = AppInitilizer()
    app_initializer.componentScan("ior_research.bean_definations")
    app_initializer.run()

    config = {
        "server": "localhost",
        "httpPort": 5001,
        "tcpPort": 16456,
    }

    clients = initializer.initializeIOTWrapper(**config);

    # Instanciate IOTClientWrapper Object,
    client1 = clients[0]
    STORE['iorClient'] = client1
    # Set on receive function, so that if a message is received this function should be called to execute some task
    # client1.set_on_receive(on_receive)

    client1.start()  # Start first client
    client1.join()

if __name__ == "__main__":
    start()