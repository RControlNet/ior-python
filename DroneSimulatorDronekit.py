import os

from numpy.core._internal import _missing_ctypes

os.environ['RCONTROLNET'] = os.getcwd() + "/iorConfigs.config"

import dronekit, time
import numpy as np
from ior_research.IOTClient import IOTClientWrapper
from queue import Queue
from threading import Thread
import threading
import ctypes
from ior_research.drone.ior_drone import Drone, get_location_from_distance, createCircle, get_distance_metres, DroneHttpClient, DroneState
from ior_research.utils.consts import DroneOperations, HOST, MissionStatus, MessageStatus
from ior_research.utils import loadConfig

config = {
    "server": HOST,
    "httpPort": 443,
    "socketServer": "10.8.0.2",
    "tcpPort": 8000,
}

copter = dronekit.connect("127.0.0.1:14551", wait_ready=True)

drone = Drone(copter)
# droneHttpClient = DroneHttpClient()
# data = loadConfig()
# username, password = data['username'], data['password']
# droneHttpClient.fetchToken(username, password)
# mission = droneHttpClient.downloadMission()
# print(mission)
# drone.mission.setWaypoints(mission['waypoints'])
# drone.mission.executeMission(drone)


def localThread():
    previousState = DroneState()
    while True:
        state = drone.getState()
        try:
            mission_status = drone.mission.getMissionState()
            syncData = {
                'heading': state.heading,
                'lat': state.position['lat'],
                'lng': state.position['lon']
            }
            if mission_status is not None:
                syncData['mission'] = mission_status
            ior_drone.sendMessage(message="", metadata=syncData, status="SYNC")
            time.sleep(5)
        except Exception as e:
            print("EXCEPTION",e)
        finally:
            previousState = state

def on_connect():
    print("connected to server")
    missionState = drone.mission.getMissionState()
    if missionState is None:
        return None
    ior_drone.sendMessage(message="SYNC", metadata=missionState, status=MessageStatus.MISSION_STATUS.name)




configFrom = config.copy()
configFrom['file'] = "from.json"
token = "default"

ior_drone = IOTClientWrapper(token=token,config=configFrom)
ior_drone.set_on_receive(lambda x: print(x))
ior_drone.setOnConnect(on_connect)

thread1 = threading.Thread(target=localThread)
thread1.start()

ior_drone.start()

drone.setClientWrapper(ior_drone)
ior_drone.join()