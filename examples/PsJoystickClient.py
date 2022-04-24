import os
import sys

from ior_research.utils.consts.envs import RCONTROLNET_ENV, RCONTOLNET_PROFILE
import json
if RCONTOLNET_PROFILE not in os.environ:
    os.environ[RCONTOLNET_PROFILE] = "receiver"

from examples.utils.client import connect, setMode, desiredAltitude, moveWithVelocity, increseAltitude, setHeading
from cndi.annotations import Autowired, AppInitilizer
import ior_research.bean_definations
from ior_research.utils.initializers import Initializer

import smbus2

ARDUINO_ADDRESS = 0x08

bus = smbus2.SMBus(1);

def write(index, value):
    bus.write_i2c_block_data(ARDUINO_ADDRESS, index, [(value >> 8) & 0xFF, value & 0xFF])
    
def on_receive(x):
    """Create a Receive message function, that takes a dict object"""
    print("Received",x['message'])
    message = json.loads(x['message'])
    try:
        throttle = int(1370 + (float(message['throttle']) * -250)) + 20
        roll = int(1500 + (float(message['roll']) * 100)) + 20
        pitch = int(1500 + (float(message['pitch']) * 100)) + 20
        yaw = int(1500 + (float(message['yaw']) * 100)) + 20
        if throttle < 1100:
            throttle = 1100;
            
        print(roll,pitch,throttle,yaw)
        write(0, roll)
        write(1, pitch)
        #write(2, throttle)
        write(3, yaw)
    except Exception as e:
        print(e)
    # try:
    #     velocity_y = message['pitch'] * -1
    #     velocity_x = message['roll']
    #     throttle = message['throttle'] * -1
    #     yaw = message['yaw']
    #
    #     if abs(throttle) > 0.3:
    #         throttle_factor = throttle * 0.05
    #         increseAltitude(throttle_factor)
    #
    #     if abs(yaw) > 0.1:
    #         setHeading(yaw * 5)
    #
    #     moveWithVelocity(vehicle, velocity_y, velocity_x)
    # except Exception as e:
    #     print(e)

initializer = None

vehicle = None

def start():
    global  vehicle
    # vehicle = connect()
    # setMode(vehicle, "GUIDED")
    # vehicle.arm(True)
    # desiredAltitude(vehicle)

    sys.path.append("../")  # Append Parent folder path to System Environment Path


    @Autowired()
    def setInitlializer(i: Initializer):
        global initializer
        initializer = i

    app_initializer = AppInitilizer()
    app_initializer.run()

    config = {
        "server": "192.168.66.5",
        "httpPort": 5001,
        "tcpPort": 8000,
    }

    clients = initializer.initializeIOTWrapper(**config);

    # Instanciate IOTClientWrapper Object,
    client1 = clients[0]

    # Set on receive function, so that if a message is received this function should be called to execute some task
    # client1.set_on_receive(on_receive)

    client1.start()  # Start first client
    client1.join()

if __name__ == "__main__":
    start()
