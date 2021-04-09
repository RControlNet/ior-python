from ior_research.mqtt import Communicator
from ior_research.IOTClient import IOTClientWrapper

client = Communicator("default", 5456)
client.connect("localhost")

config = {
    "server": "localhost",
    "httpPort": 5001,
    "tcpPort": 8000,
}

configFrom = config.copy()
configFrom['file'] = "../../config/to.json"
token = "default"

def on_receive(msg):
    print(msg)
    message = msg['message']
    for (key,value) in msg['syncData'].items():
        client.sendMessage(sm=key + "/" +str(value))


t1 = IOTClientWrapper(token=token ,config=configFrom)

t1.set_on_receive(fn = on_receive)
t1.start()
t1.join()