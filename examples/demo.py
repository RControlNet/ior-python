from IOTClient import IOTClient

token = ""
from_code = int("current device code here")
to = int("receiver code here")

def on_receive(msg):
    """Called when ever some data is received"""
    print(msg)

t1 = IOTClient(code=from_code,to = to,token = token,debug=False)
t1.set_on_receive(fn = on_receive)
t1.start()