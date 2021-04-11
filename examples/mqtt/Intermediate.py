from ior_research.mqtt import Communicator
from ior_research.IOTClient import IOTClientWrapper
from ior_research.drone.ior_drone import DroneOperations, map_name_drone_attribute
from ior_research.utils.video import createVideoTransmitter
import os

import argparse

if __name__ == "__main__":
    os.environ['RCONTROLNET'] = "../../config/iorConfigs.config"
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="localhost", type=str)
    parser.add_argument("--broker", default="localhost", type=str)

    args = parser.parse_args()
    client = Communicator("default", 5456)
    client.connect(args.broker)

    config = {
        "server": args.server,
        "httpPort": 5001,
        "tcpPort": 8000,
    }

    configFrom = config.copy()
    configFrom['file'] = "../../config/to.json"
    token = "default"
    videoTransmitter = None

    def on_receive(msg):
        global videoTransmitter
        message = msg['message']
        if map_name_drone_attribute(message,DroneOperations.START_STREAMER):
            if videoTransmitter is None:
                videoTransmitter = createVideoTransmitter()

            if not videoTransmitter.checkBrowserAlive():
                videoTransmitter.openBrowserAndHitLink()
            else:
                videoTransmitter.close()
                videoTransmitter = createVideoTransmitter()
                videoTransmitter.openBrowserAndHitLink()

        else:
            for (key,value) in msg['syncData'].items():
                client.sendMessage(sm=key + "/" +str(value))


    t1 = IOTClientWrapper(token=token ,config=configFrom)

    t1.set_on_receive(fn = on_receive)
    t1.start()
    t1.join()