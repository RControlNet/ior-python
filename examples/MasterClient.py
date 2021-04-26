from pynput.keyboard import Listener, Key, KeyCode # For Keyboard listener
from ior_research.IOTClient import IOTClientWrapper # For connect and send messages to the controlnet

"""
Define the config for the IOTClientWrapper, it will be used to connect to the specific server and port those are bind to the tunnel server 
"""
config = {
        "server": "10.8.0.2",
        "httpPort": 5001,
        "tcpPort": 8000,
    }

configFrom = config.copy()
configFrom['file'] = "../config/from.json" # Very Important, this file determines the client configurations

token = "default"

def on_receive(msg):
    """
    On message receive function, whenever a message is received this function is called
    """
    print(msg)

t1 = IOTClientWrapper(token=token ,config=configFrom) # Instanciate IOTClientWrapper Object

t1.set_on_receive(fn = on_receive) # Set on receive function
t1.start() # Start the Client

previous = None
def on_press(key):
    """
    Determines which key is pressed on the keyboard
    """
    global previous

    if previous == key:
        return None

    metadata = dict()
    if key == KeyCode.from_char(char='w'):
        metadata["D"] = 1
    elif key == KeyCode.from_char(char='s'):
        metadata["U"] = 1
    elif key == KeyCode.from_char(char='a'):
        metadata["R"] = 1
    elif key == KeyCode.from_char(char='d'):
        metadata["L"] = 1

    if len(metadata) > 0:
        print(metadata)
        t1.sendMessage(message="CONTROL",metadata=metadata) # Send the command to other side
        previous = key

def on_release(key):
    """
    Determines which key is released on the keyboard
    """
    metadata = dict()
    if key == KeyCode.from_char(char='w'):
        metadata["D"] = 0
    elif key == KeyCode.from_char(char='s'):
        metadata["U"] = 0
    elif key == KeyCode.from_char(char='a'):
        metadata["R"] = 0
    elif key == KeyCode.from_char(char='d'):
        metadata["L"] = 0
    if len(metadata) > 0:
        t1.sendMessage(message="CONTROL",metadata=metadata) # Sends the command to other side
        global previous
        previous = None

    if key == Key.esc:
        t1.terminate() # Terminate client and Exit
        exit(0);


listener = Listener(on_release=on_release,on_press = on_press) # Instanciate Keyboard Listener Object
listener.start() # Start listening to keyboard Inputs

