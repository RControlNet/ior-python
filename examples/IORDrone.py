import os,sys
from typing import Type
import time
from cndi.annotations import AppInitilizer, Autowired
from dronekit import connect, VehicleMode

from ior_research.utils.consts.envs import RCONTROLNET_ENV, RCONTROLNET_LOG_LEVEL
from ior_research.utils.filterchains import MessageFilterChain
from ior_research.utils.initializers import Initializer


import logging

if RCONTROLNET_LOG_LEVEL not in os.environ:
    os.environ[RCONTROLNET_LOG_LEVEL] = str(logging.INFO)

logging.basicConfig(format=f'%(asctime)s - %(name)s - %(message)s', level=int(os.environ[RCONTROLNET_LOG_LEVEL]))
logger = logging.getLogger(__name__)

initializer: Type[Initializer] = None

class CustomMessageFilter(MessageFilterChain):
    def doFilter(self, message):
        print(message)

def boot():
    if RCONTROLNET_ENV not in os.environ:
        os.environ[RCONTROLNET_ENV] = "../config/iorConfigs.yml"

    @Autowired()
    def setObjects(init: Initializer):
        global initializer
        initializer = init

    app = AppInitilizer()
    app.componentScan("ior_research.bean_definations")
    app.run()

    initializer.addFilter(CustomMessageFilter(initializer))

    uav = connect("192.168.66.5:14550", wait_ready=True)
    uav.mode = VehicleMode("GUIDED")
    while uav.mode.name != "GUIDED":
        print("Vehicle not in GUIDED")
        uav.mode = VehicleMode("GUIDED")
        time.sleep(1)

    (client, ) = initializer.initializeIOTWrapper()
    client.start()

    while True:
        location = uav.location.global_frame
        print(location)
        syncData = {
            "lat": str(location.lat),
            "lng": str(location.lon),
            "heading": str(uav.heading)
        }

        client.sendMessage(message="ABC", metadata=syncData)
        time.sleep(1)




if __name__ == "__main__":
    boot()
