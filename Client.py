from IOTClient import IOTClient

token = "c7024ca7-57a2-4c89-978c-121fb8152312"
#token = "4eafc05a-a049-4b1b-a989-5b431f8bdbc1"
fromCode = 1234
to = 555
port = 8000

speed = 500

from ev3dev.ev3 import *

motorB = LargeMotor('outB');
motorC = LargeMotor('outC');

def on_receive(msg):
    if "syncData" not in msg:
        return None
    global speed
    data = msg["syncData"]

    if "INC" in data:
        speed +=  10 * int(data["INC"])
        if speed > 1000:
            speed = 1000
            client.sendMessage("Speed Reached to 1000")
        client.__writeline("Motor Speed set to: %d"%speed)
    elif "DEC" in data:
        speed -= 10 * int(data["DEC"])
        if speed < 0:
            speed = 0
            client.sendMessage("Speed Reached to 0")
        client.__writeline("Motor Speed set to: %d" % speed)

    if "UP" in data:
        if int(data["UP"]) == 1:
            motorB.run_forever(speed_sp=speed)
            motorC.run_forever(speed_sp=speed)
        else:
            motorB.run_forever(speed_sp=0)
            motorC.run_forever(speed_sp=0)

    if "DOWN" in data:
        if int(data["DOWN"]) == 1:
            motorB.run_forever(speed_sp=-speed)
            motorC.run_forever(speed_sp=-speed)
        else:
            motorB.run_forever(speed_sp=00)
            motorC.run_forever(speed_sp=00)

    if "LEFT" in data:
        if int(data["LEFT"]) == 1:
            motorB.run_forever(speed_sp=speed)
            motorC.run_forever(speed_sp=-speed)
        else:
            motorB.run_forever(speed_sp=00)
            motorC.run_forever(speed_sp=00)

    if "RIGHT" in data:
        if int(data["RIGHT"]) == 1:
            motorB.run_forever(speed_sp=-speed)
            motorC.run_forever(speed_sp=speed)
        else:
            motorB.run_forever(speed_sp=00)
            motorC.run_forever(speed_sp=00)

try:
    client = IOTClient(code=fromCode,to = to,token = token,time_delay = int(60*1.5),debug=True)
    client.set_on_receive(fn=on_receive)
    client.start()
    client.join()
except KeyboardInterrupt:
    exit(-1)