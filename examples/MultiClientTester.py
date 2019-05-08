from ior_research.IOTClient import IOTClient
from time import sleep
from threading import Thread

token = ""

def on_receive(msg):
    print(msg)

def processRequest(code,to):
    client = IOTClient(code,token,to,10,debug=True)
    client.set_on_receive(fn=on_receive)
    client.start()
    sleep(1)
    while True:
        client.sendMessage("Hey From %d"%code)
        sleep(6)

t1 = Thread(target=processRequest,args=(1234,555))
t2 = Thread(target=processRequest,args=(555,1234))

t1.start()
t2.start()