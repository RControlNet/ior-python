from ior_research.utils.proxy import ProxyServer
"""
from ev3dev.ev3 import *

motorB = LargeMotor('outB');
motorC = LargeMotor('outD');
motorA = MediumMotor('outA');
"""

def on_receive(msg):
    print(msg)
    return None

    if "syncData" not in msg:
        print(msg)
        return None

    global speed
    data = msg["syncData"]
    if "S" in data:
        current_pos = int(data["S"]) * 2.5
        motorA.run_to_abs_pos(position_sp=current_pos, speed_sp=100)

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