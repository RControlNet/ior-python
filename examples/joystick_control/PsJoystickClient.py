import os

from cndi.binders.message import Input
from cndi.env import loadEnvFromFile, getContextEnvironment, VARS
from cndi.initializers import AppInitilizer
from cndi.resources import ResourceFinder

from ior_research.IOTClient import IOTClientWrapper
from ior_research.utils.consts.envs import RCONTOLNET_PROFILE
import json

if RCONTOLNET_PROFILE not in os.environ:
    os.environ[RCONTOLNET_PROFILE] = "receiver"

from cndi.annotations import Autowired
from ior_research.utils.initializers import Initializer


STORE = dict(initializer=None,
             iorClient=None)

vehicle = None
DEFAULT_CHANNEL = "mqtt-to-ior-channel"

@Input(DEFAULT_CHANNEL)
def handleInputMessage(message):
    client: IOTClientWrapper = STORE['iorClient']
    if client is not None:
        message = json.loads(message.payload.decode())
        print(message)
        data = dict(
            message=message['message'],
            metadata= message['syncData'] if 'syncData' in message else dict()
        )
        client.sendMessage(**data)

def start():
    global  vehicle

    @Autowired()
    def setInitializer(i: Initializer):
        global initializer
        STORE['initializer'] = i
        initializer = i

    resourcePath = ResourceFinder().findResource("receiver.yml")

    loadEnvFromFile(resourcePath)
    app_initializer = AppInitilizer()
    app_initializer.componentScan("ior_research.bean_definations")
    app_initializer.run()

    config = {
        "server": getContextEnvironment("rcn.ior.host",defaultValue="localhost"),
        "httpPort": getContextEnvironment("rcn.ior.httpPort", defaultValue=5001, castFunc=int),
        "tcpPort": getContextEnvironment("rcn.ior.tcpPort", defaultValue=16456, castFunc=int)
    }

    clients = initializer.initializeIOTWrapper(**config);
    # Instanciate IOTClientWrapper Object,
    client1 = clients[0]
    STORE['iorClient'] = client1

    client1.start()  # Start first client
    client1.join()

if __name__ == "__main__":
    start()