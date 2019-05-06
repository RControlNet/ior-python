from ior_research.IOTClient import IOTClient

#token = "c7024ca7-57a2-4c89-978c-121fb8152312"
token = "4eafc05a-a049-4b1b-a989-5b431f8bdbc1"

fromCode = 1234
to = 789

speed = 500

from ev3dev.ev3 import *

motorB = LargeMotor('outB');
motorC = LargeMotor('outD');
motorA = MediumMotor('outA');

def on_receive(msg):
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

try:
    client = IOTClient(code=fromCode,to = to,token = token,time_delay = int(60*1.5),debug=True)
    client.set_on_receive(fn=on_receive)
    client.start()
    client.join()
except KeyboardInterrupt:
    motorB.stop()
    motorC.stop()
    exit(-1)