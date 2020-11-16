from ior_research.IORTransmitter import Transmitter

from threading import Thread
import pygame
import time
"""
from keras.layers import Input, Reshape, Conv2D, UpSampling2D
from keras.models import Model
import cv2
#from imagezmq.imagezmq import imagezmq


image_hub = imagezmq.ImageHub()

def load_model():
    decoder_input = Input(shape=( 38400,))
    decoder = Reshape((60, 80, 8))(decoder_input)
    decoder = Conv2D(64, (3, 3), activation='relu', padding='same')(decoder)
    decoder = UpSampling2D((2, 2), interpolation='bilinear')(decoder)
    decoder = Conv2D(32, (3, 3), activation='relu', padding='same')(decoder)
    decoder = UpSampling2D((2, 2), interpolation='bilinear')(decoder)
    decoder = Conv2D(16, (3, 3), activation='relu', padding='same')(decoder)
    decoder = UpSampling2D((2, 2), interpolation='bilinear')(decoder)
    decoder = Conv2D(8, (3, 3), activation='relu', padding='same')(decoder)
    decoder = Conv2D(3, (3, 3), activation='relu', padding='same')(decoder)

    decoder_model = Model(decoder_input, decoder)
    decoder_model.load_weights('./../5-decoder.h5')
    return decoder_model

def videoThread():
    decoder_model = load_model()

    while True:  # show streamed images until Ctrl-C
        rpi_name, image = image_hub.recv_image()
        image_hub.send_reply(b'OK')
        image = decoder_model.predict(image)[0]/255
        cv2.imshow(rpi_name, image) # 1 window for each RPi
        cv2.waitKey(1)

video_thread = Thread(target=videoThread)
#video_thread.start()
#video_thread.join()
"""
pygame.display.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
x = joysticks[0]
x.init()

token = "ce84fbd8-1f83-4bc2-8754-e44f148718cd"
fromCode = 1456
to = 7896


t1 = Transmitter(code=fromCode,to = to,token = token,debug=True,server='192.168.1.3')
print("Sleeping")
t1.waitForReceiver()
t1.start()

print("Wake UP")
values = [0,0,0,0]

def map(input,adder=1,mul=50):
    input = input + adder
    out = input * mul
    return int(out)

while True:
    pygame.event.pump()
    for i in range(3):
        values[i] = map(x.get_axis(i), adder=1.001) * 10 + 10
    values[3] = map(x.get_axis(5), adder=1.001) * 10 + 10

    for i in range(len(values)):
        values[i] = i * 1000 + values[i]
        t1.sendData("%d\n"%values[i])
    print(values)
    time.sleep(0.05)
