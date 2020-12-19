from pynput.keyboard import Listener, Key, KeyCode
from ior_research.IOTClient import IOTClientWrapper

config = {
        "server": "localhost",
        "httpPort": 5001,
        "tcpPort": 8000,
    }

configFrom = config.copy()
configFrom['file'] = "C:\\Users\\Asus\\Downloads\\5fda54447e5593227072b6b30.json"
token = "a9b08f66-8e6f-4558-b251-da7163aac420"


def on_receive(msg):
    print(msg)

t1 = IOTClientWrapper(token=token ,config=configFrom)

t1.set_on_receive(fn = on_receive)
t1.start()

previous = None
def on_press(key):
    global previous

    if previous == key:
        return None
    metadata = dict()
    if key == KeyCode.from_char(char='w'):
        metadata["U"] = 1
    elif key == KeyCode.from_char(char='s'):
        metadata["D"] = 1
    elif key == KeyCode.from_char(char='a'):
        metadata["L"] = 1
    elif key == KeyCode.from_char(char='d'):
        metadata["R"] = 1

    if len(metadata) > 0:
        print(metadata)
        t1.sendMessage(message="CONTROL",metadata=metadata)
        previous = key

def on_release(key):
    metadata = dict()
    if key == KeyCode.from_char(char='w'):
        metadata["U"] = 0
    elif key == KeyCode.from_char(char='s'):
        metadata["D"] = 0
    elif key == KeyCode.from_char(char='a'):
        metadata["L"] = 0
    elif key == KeyCode.from_char(char='d'):
        metadata["R"] = 0
    if len(metadata) > 0:
        t1.sendMessage(message="CONTROL",metadata=metadata)
        global previous
        previous = None

    if key == Key.esc:
        t1.terminate()
        exit(0);


listener = Listener(on_release=on_release,on_press = on_press)
listener.start()

