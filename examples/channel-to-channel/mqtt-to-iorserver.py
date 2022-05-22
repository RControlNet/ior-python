import json
import os
from time import sleep

from ior_research.IOTClient import IOTClientWrapper

os.environ['RCN_ENVS_CONFIG.active.profile'] = "mqtt-to-iorserver"

from cndi.binders.message import Input
from cndi.env import loadEnvFromFile
from cndi.initializers import AppInitilizer

DEFAULT_CHANNEL = "mqtt-to-ior-channel"

STORE = dict(client=None)

@Input(DEFAULT_CHANNEL)
def handleInputMessage(message):
    print(message.payload)
    client: IOTClientWrapper = STORE['client']
    if client is not None:
        message = json.loads(message.payload.decode())
        data = dict(
            message=message['message'],
            metadata=message['syncData']
        )
        client.sendMessage(data)


if __name__ == '__main__':
    loadEnvFromFile("../../resources/channel-to-channel.yml")

    app_initializer = AppInitilizer()
    app_initializer.componentScan("ior_research.bean_definations")
    app_initializer.run()

    while True:
        sleep(10)b