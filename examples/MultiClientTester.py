from ior_research.IOTClient import IOTClient
from time import sleep
from threading import Thread

#token = "c7024ca7-57a2-4c89-978c-121fb8152312";
token = "4eafc05a-a049-4b1b-a989-5b431f8bdbc1"

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