from ior_research.IOTClient import IOTClientWrapper
import time

def on_receive(x):
    print("Received",time.time() - float(x['message']))

if __name__ == "__main__":
    config = {
        "server": "cloud.controlnet.ml",
        "httpPort": 443,
        "socketServer": "localhost",
        "tcpPort": 8000,
    }

    configFrom = config.copy()
    configFrom['file'] = "../from.json"
    configTo = config.copy()
    configTo['file'] = "../to.json"

    token = "default"

    client1 = IOTClientWrapper(token,config=configFrom)
    client2 = IOTClientWrapper(token,config=configTo)
    client2.set_on_receive(on_receive)

    client1.start()
    client2.start()
    #client2.join()

    while True:
        print("Sending Message")
        client1.sendMessage(message = str(time.time()))
        time.sleep(0.1)

    time.sleep(5)

    client1.join()
    client2.join()

    client1.close()
    client2.close()