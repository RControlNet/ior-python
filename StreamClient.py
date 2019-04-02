from IOTClient import IOTClient
token = "4eafc05a-a049-4b1b-a989-5b431f8bdbc1"
fromCode = 555
to = 1234
server = "localhost"
port = 8000
import numpy as np
import cv2
def on_receive(msg):
    print(msg)
    if "syncData" not in msg:
        return None

    data = msg["syncData"]
    print(data)
    return None
    if "camera" in data:
        frame = np.array(data['camera'])
        cv2.imshow('client',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            client.close()

client = IOTClient(code=fromCode,to = to,token = token,server=server,port=port,time_delay = 5*1000)
client.set_on_receive(fn=on_receive)
client.start()
client.join()