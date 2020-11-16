from ior_research.IOTClient import IOTClient

import pygame
import time

pygame.display.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
x = joysticks[0]
x.init()
print(x.get_numaxes())
print(x.get_name())

token = "826f7556-6442-4c09-9e1e-76dbb462542c"
fromCode = 1456
to = 7896


t1 = IOTClient(code=fromCode,to = to,token = token,debug=True,isTunneled=True,server='192.168.1.12')
sock = t1.getSocket()
writefile = sock.makefile('w')

values = [0,0,0,0]

def map(input,adder=1,mul=50):
    input = input + adder
    out = input * mul
    return int(out)
throttle = 88

while True:
    pygame.event.pump()
    values[3] = map(x.get_axis(0),adder=1.001)* 10 + 5
    values[0] = map(x.get_axis(2),adder=1.001)* 10 + 5
    values[1] = map(x.get_axis(3) * -1)*10 + 5

    throttle += map(x.get_axis(1),adder=0,mul=-10)

    if throttle <= 88:
        throttle = 88
    elif throttle > 750:
        throttle = 750

    values[2] = throttle

    print(values)
    for i in range(4):
        value = values[i]
        if value < 88:
            value = 88
        elif value > 990:
            value = 990
        value = value + i * 1000

        writefile.write("%d\n" % (value))
    writefile.flush()

    time.sleep(0.05)
