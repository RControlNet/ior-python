from ior_research.utils.proxy import ProxyClient
from ior_research.IOTClient import IOTClientWrapper
import json

config = {
    "server": "localhost",
    "httpPort": 5001,
    "tcpPort": 8000
}

token = "a9b08f66-8e6f-4558-b251-da7163aac420"
code = 789
to = 1234

def on_receive(msg):
    msg = json.dumps(msg)
    proxyClient.sendData(msg.encode())

def on_send(msg):
    print("Send",msg)

proxyClient = ProxyClient()
proxyClient.connect(callback=on_send, server=("localhost", 54753))
proxyClient.start()

t2 = IOTClientWrapper(token,code,to,config=config)

t2.set_on_receive(fn = on_receive)
t2.start()