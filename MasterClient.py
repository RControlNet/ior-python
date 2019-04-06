from pynput.keyboard import Listener, Key, KeyCode
import time
from IOTClient import IOTClient

token = "c7024ca7-57a2-4c89-978c-121fb8152312"
#token = "4eafc05a-a049-4b1b-a989-5b431f8bdbc1"

fromCode = 555
to = 1234

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
        metadata["INC"] = 1
    elif key == Key.down:
        metadata["DEC"] = 1
    elif key == KeyCode.from_char(char='w'):
        metadata["UP"] = 1
    elif key == KeyCode.from_char(char='s'):
        metadata["DOWN"] = 1
    elif key == KeyCode.from_char(char='a'):
        metadata["LEFT"] = 1
    elif key == KeyCode.from_char(char='d'):
        metadata["RIGHT"] = 1

    if len(metadata) > 0:
        print(metadata)
        t1.sendMessage(message="CONTROL",metadata=metadata)
        previous = key

def on_release(key):
    metadata = dict()
    if key == KeyCode.from_char(char='w'):
        metadata["UP"] = 0
    elif key == KeyCode.from_char(char='s'):
        metadata["DOWN"] = 0
    elif key == KeyCode.from_char(char='a'):
        metadata["LEFT"] = 0
    elif key == KeyCode.from_char(char='d'):
        metadata["RIGHT"] = 0
    if len(metadata) > 0:
        t1.sendMessage(message="CONTROL",metadata=metadata)
        global previous
        previous = None

    if key == Key.esc:
        t1.close()
        return False

with Listener(on_release=on_release,on_press = on_press) as listener:
    listener.join()
