import sys, os

sys.path.append(os.getcwd())
from ior_research.utils.proxy import ProxyClient
from ior_research.IOTClient import IOTClientWrapper
from ior_research.utils.video import VideoTransmitter, createVideoTransmitter
import json

config = {
    "server": "192.168.0.131",
    "httpPort": 5001,
    "tcpPort": 8000
}

token = "a9b08f66-8e6f-4558-b251-da7163aac420"
code = 789
to = 1234
videoTransmitter = None

def on_receive(msg):
    global videoTransmitter
    if(msg['message'] is not None and msg['message'] == "START_STREAMER"):
        videoTransmitter = createVideoTransmitter()
        videoTransmitter.openBrowserAndHitLink("mayank31313@gmail.com", "12345678")
    if(videoTransmitter is not None and msg['message'] is not None and msg['message'] == "STOP_STREAMER"):
        videoTransmitter.quit()

    msg = json.dumps(msg)
    print(msg)
#    proxyClient.sendData(msg.encode())

def on_send(msg):
    print("Send",msg)

#proxyClient = ProxyClient()
# proxyClient.connect(callback=on_send, server=("10.42.1.95", 54753))
# proxyClient.start()

t2 = IOTClientWrapper(token,code,to,config=config)

t2.set_on_receive(fn = on_receive)
t2.start()