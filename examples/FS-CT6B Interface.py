from ior_research.IOTClient import IOTClient

import pygame
import time

import cv2
from imagezmq.imagezmq import imagezmq

from threading import Thread

image_hub = imagezmq.ImageHub()

def videoThread():
    while True:  # show streamed images until Ctrl-C
        rpi_name, image = image_hub.recv_image()
        image_hub.send_reply(b'OK')
        cv2.imshow(rpi_name, image) # 1 window for each RPi
        cv2.waitKey(1)

video_thread = Thread(target=videoThread)
#video_thread.start()

pygame.display.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
x = joysticks[0]
x.init()

token = "826f7556-6442-4c09-9e1e-76dbb462542c"
fromCode = 1456
to = 7896


t1 = IOTClient(code=fromCode,to = to,token = token,debug=True,isTunneled=True,server='192.168.1.3')
sock = t1.getSocket()
writefile = sock.makefile('w')

values = [0,0,0,0]

def map(input,adder=1,mul=50):
    input = input + adder
    out = input * mul
    return int(out)

while True:
    pygame.event.pump()
    for i in range(3):
        values[i] = map(x.get_axis(i), adder=1.001) * 10
    values[3] = map(x.get_axis(5), adder=1.001) * 10

    for i in range(len(values)):
        values[i] = i * 1000 + values[i]
        writefile.write("%d\n"%values[i])
    writefile.flush()
    print(values)
    time.sleep(0.05)
