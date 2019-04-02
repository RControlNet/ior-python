from IOTClient import  IOTClient
from time import sleep
from threading import Thread

token = "4eafc05a-a049-4b1b-a989-5b431f8bdbc1";

def on_receive(msg):
    print(msg)

def processRequest(code,to):
    client = IOTClient(code,token,to,10)
    client.set_on_receive(fn=on_receive)
    client.start()
    sleep(1)
    while True:
        client.sendMessage("Hey From %d"%code)
        sleep(6)

t1 = Thread(target=processRequest,args=(789,555))
t2 = Thread(target=processRequest,args=(555,789))

t1.start()
t2.start()