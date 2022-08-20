import json
import os
from time import sleep

from cndi.annotations import Autowired

from ior_research.IOTClient import IOTClientWrapper
from ior_research.utils.consts.envs import RCONTOLNET_PROFILE
from ior_research.utils.initializers import Initializer

os.environ['RCN_ENVS_CONFIG.active.profile'.lower()] = "mqtt-to-iorserver"
if RCONTOLNET_PROFILE not in os.environ:
    os.environ[RCONTOLNET_PROFILE] = "sender"

from cndi.binders.message import Input
from cndi.env import loadEnvFromFile, getContextEnvironment
from cndi.initializers import AppInitilizer

STORE = dict(client=None)

@Autowired()
def setInitializer(initializer: Initializer):
    STORE['initializer'] = initializer

    server = getContextEnvironment("rcn.ior.server.host", defaultValue="localhost")
    tcpPort = getContextEnvironment("rcn.ior.server.tcpport", defaultValue=8000, castFunc=int)
    httpPort = getContextEnvironment("rcn.ior.server.httpport", defaultValue=5001, castFunc=int)

    config = {
        "server": server,
        "httpPort": httpPort,
        "tcpPort": tcpPort,
    }

    STORE['client'] = initializer.initializeIOTWrapper(**config)[0]
    STORE['client'].set_on_receive(print)
    STORE['client'].start()

@Input("mqtt-to-ior-channel")
def handleInputMessage(message):
    print(message.payload)
    client: IOTClientWrapper = STORE['client']
    if client is not None:
        message = json.loads(message.payload.decode())
        data = dict(
            message=message['message'],
            metadata=message['syncData']
        )
        client.sendMessage(**data)


if __name__ == '__main__':
    loadEnvFromFile("../../resources/channel-to-channel.yml")

    app_initializer = AppInitilizer()
    app_initializer.componentScan("ior_research.bean_definations")
    app_initializer.run()

    while True:
        sleep(10)