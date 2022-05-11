from time import sleep

from cndi.annotations import Autowired
from paho.mqtt.client import MQTTMessage

from ior_research.utils.consts import DroneOperations

from ior_research.utils.initializers import Initializer
from ior_research.utils.text import socketMessageSchema

from cndi.binders.message import Input
from cndi.env import loadEnvFromFile
from cndi.initializers import AppInitilizer

STATE_STORE = dict(initializer=None)

@Autowired()
def setInitializer(initializer: Initializer):
    STATE_STORE['initializer'] = initializer

@Input("video-message-input")
def handleVideoMessage(message: MQTTMessage):
    initializer:Initializer = STATE_STORE['initializer']
    message = socketMessageSchema.loads(message.payload.decode())

    if message.message == DroneOperations.START_STREAMER.name:
        if initializer.transmitter is None:
            initializer.initializeVideoTransmitter()
        elif initializer.transmitter.checkBrowserAlive():
            initializer.transmitter.close()
        initializer.transmitter.openBrowserAndHitLink()

    if message.message == DroneOperations.STOP_STREAMER.name:
        if initializer.transmitter is not None and initializer.transmitter.checkBrowserAlive():
            initializer.transmitter.close()
        initializer.transmitter = None

if __name__ == "__main__":
    loadEnvFromFile("../resources/videoTransmitter.yaml")
    appInitializer = AppInitilizer()
    appInitializer.componentScan("ior_research.bean_definations.mqtt")
    appInitializer.run()

    while True:
        sleep(10)