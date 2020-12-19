import sys, os

sys.path.append(os.getcwd())

from ior_research.utils.proxy import ProxyServer
import time
from ev3dev.ev3 import *

motorB = LargeMotor('outB')
motorC = LargeMotor('outC')

motorC.run_forever(speed_sp=100)
time.sleep(5)
motorC.stop()
#motorA = MediumMotor('outA');

speed = 100
def on_receive(msg):
    print(msg)

    if "syncData" not in msg or msg["syncData"] is None:
        return None

    global speed
    data = msg["syncData"]
    if "S" in data:
        current_pos = int(data["S"]) * 2.5
        #motorA.run_to_abs_pos(position_sp=current_pos, speed_sp=100)

    if "U" in data:
        if int(data["U"]) == 1:
            motorB.run_forever(speed_sp=speed)
            motorC.run_forever(speed_sp=speed)
        else:
            motorB.stop()
            motorC.stop()

    if "D" in data:
        if int(data["D"]) == 1:
            motorB.run_forever(speed_sp=-speed)
            motorC.run_forever(speed_sp=-speed)
        else:
            motorB.stop()
            motorC.stop()

    if "R" in data:
        if int(data["R"]) == 1:
            motorB.run_forever(speed_sp=speed)
            motorC.run_forever(speed_sp=-speed)
        else:
            motorB.stop()
            motorC.stop()

    if "L" in data:
        if int(data["L"]) == 1:
            motorB.run_forever(speed_sp=-speed)
            motorC.run_forever(speed_sp=speed)
        else:
            motorB.stop()
            motorC.stop()


server = ProxyServer(server=('', 54753), callback=on_receive)
server.start()
server.join()