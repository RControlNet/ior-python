from ior_research.mqtt import Communicator, createClient
from ior_research.IOTClient import IOTClientWrapper
import time

def run():
    config = {
        "server": "cloud.controlnet.ml",
        "httpPort": 443,
        "socketServer": "localhost",
        "tcpPort": 8000,
        "file": "../../to.json"
    }

    token = "default"
    receiver = IOTClientWrapper(config=config, token=token)

    code = "1234"
    client = createClient(token, code)

    receiver.set_on_receive(lambda x: client.sendMessage(x))

    receiver.start()
    receiver.join()

if __name__ == "__main__":
    run()