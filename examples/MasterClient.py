from pynput.keyboard import Listener, Key, KeyCode
import time
from ior_research.IOTClient import IOTClient


token = "1db93bcd-15a9-48be-8a35-f7f805cee03b"

fromCode = 1234
to = 555

def on_receive(msg):
    print(msg)

t1 = IOTClient(code=fromCode,to = to,token = token,debug=True)
t1.set_on_receive(fn = on_receive)
t1.start()

previous = None
def on_press(key):
    global previous

    if previous == key:
        return None
    metadata = dict()
    if key == Key.up:
        metadata["I"] = 1
    elif key == Key.down:
        metadata["D"] = 1
    elif key == KeyCode.from_char(char='w'):
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
        t1.close()
        return False

with Listener(on_release=on_release,on_press = on_press) as listener:
    listener.join()
