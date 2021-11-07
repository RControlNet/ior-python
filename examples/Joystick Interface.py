import pygame
import time

pygame.display.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
x = joysticks[0]
x.init()

print(x.get_numaxes())
print(x.get_name())
print(x.get_numbuttons())

values = [0 for _ in range(x.get_numaxes())]

while True:
    pygame.event.pump()
    for i in range(x.get_numaxes()):
        values[i] = x.get_axis(i) * 0.369

    print(values)
    time.sleep(0.1)
