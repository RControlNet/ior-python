from ior_research.IOTClient import IOTClientWrapper
import time

def run():
    config = {
        "server": "cloud.controlnet.ml",
        "httpPort": 443,
        "socketServer": "localhost",
        "tcpPort": 8000,
        "file": "../../from.json"
    }

    token = "default"
    sender = IOTClientWrapper(config=config, token=token)
    sender.set_on_receive(lambda x: print("Received Message",x))

    sender.start()
    while True:
        sender.sendMessage(message=str(time.time()))
        time.sleep(2)

if __name__ == "__main__":
    run()