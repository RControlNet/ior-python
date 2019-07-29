from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

from ior_research.IOTClient import IOTClient
from queue import Queue
from threading import Thread

import time

token = "826f7556-6442-4c09-9e1e-76dbb462542c"

fromCode = 1456
to = 7896

throttle = 88
aileron=500
elevator=500
rudder=500



t1 = IOTClient(code=fromCode,to = to,token = token,debug=True,isTunneled=True,server='192.168.1.13')
queue = Queue()

sock = t1.getSocket()

def sendingThread():
    while True:
        if queue.not_empty:
            sock.send(str(queue.get()).encode() + b"\n")
            time.sleep(0.1)

t2 = Thread(target=sendingThread)
t2.start()

def on_press(key):
    global aileron,rudder,elevator

    if key == KeyCode.from_char(char='4'):
        aileron -= 10
        if aileron < 0:
            aileron = 0
        queue.put(aileron)

    if key == KeyCode.from_char(char='6'):
        aileron += 10
        if aileron > 1000:
            aileron = 1000
        queue.put(aileron)

    if key == KeyCode.from_char(char='8'):
        elevator -= 10
        if elevator < 200:
            elevator = 200
        queue.put(elevator + 1000)

    if key == KeyCode.from_char(char='2'):
        elevator += 10
        if elevator > 789:
            elevator = 789
        queue.put(elevator + 1000)


    if key == KeyCode.from_char(char='a'):
        rudder -= 100
        if rudder < 116:
            rudder = 116
        queue.put(rudder + 3000)

    if key == KeyCode.from_char(char='d'):
        rudder += 100
        if rudder > 789:
            rudder = 789
        queue.put(rudder + 3000)




def on_release(key):
    global throttle, aileron, rudder, elevator
    if key == KeyCode.from_char(char='4') or key == KeyCode.from_char(char='6'):
        aileron = 500
        queue.put(aileron)

    if key == KeyCode.from_char(char='2') or key == KeyCode.from_char(char='8'):
        elevator = 500
        queue.put(elevator + 1000)

    if key == KeyCode.from_char(char='a') or key == KeyCode.from_char(char='d'):
        rudder = 500
        queue.put(rudder + 3000)



    if key == Key.esc:
        sock.send(str(3500).encode() + b'\n')
        sock.send(str(1500).encode() + b'\n')
        sock.send(str(2100).encode() + b'\n')
        sock.send(str(500).encode() + b'\n')

        t1.close()
        exit(0);

def on_scroll(x, y, dx, dy):
    global throttle
    throttle += 10 * dy
    if throttle > 789:
        throttle = 789
    if throttle < 88:
        throttle = 88
    queue.put(throttle + 2000)

mouse_listener = MouseListener(on_scroll=on_scroll)
mouse_listener.start()

keyboard_listener = KeyboardListener(on_release=on_release,on_press=on_press)
keyboard_listener.start()

mouse_listener.join()
keyboard_listener.join()