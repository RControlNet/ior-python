from  mavsdk import System
import asyncio
from ior_research import IOTClient, IOTClientWrapper
from asyncio.events import get_event_loop, new_event_loop, set_event_loop
import time
from mavsdk.telemetry import LandedState, Position
from ior_research.drone.ior_drone import get_distance_metres, DroneState, DroneOperations, quaternion_to_euler_angle_vectorized, get_bearing, IORPosition, IOTFunctionUtils
import enum, threading, math
import numpy as np
import requests
from concurrent.futures import ProcessPoolExecutor
from queue import  Queue

from


def wait(sleep):
    lap = time.time()
    def test(state):
        print(time.time() - lap)
        return (time.time() - lap) > sleep
    return test

class IORStateMatrix:
    def __init__(self):
        self.state = DroneState()
        self.holds = Queue()
        self.counter = 0

    def getState(self):
        return self.state

    def pushAsyncMethod(self, fn: IOTFunctionUtils):
        self.counter += 1
        self.holds.put((self.counter, fn))
        return self.counter

    def getAsync(self):
        if(self.holds.empty() == True):
            return (None, None)
        return self.holds.get()

class MavDrone(threading.Thread):
    def __init__(self, copter: System, connector: IOTClientWrapper = None, httpClient: DroneHttpClient = None):
        threading.Thread.__init__(self)

        self.copter = System()
        self.holdAndWaitLoop = get_event_loop()
        self.stateMatrix = IORStateMatrix()
        self.onReceive = None
        self.connector = connector
        self.httpClient = httpClient
        self.holdAndWaitLoop.run_until_complete(self.copter.connect())

        self.fn = None
        self.currentTask = None
        self.currentState = False
        self.currentId = None
        self.currentWait = None

        self.start()
        if(self.connector is not None):
            self.connector.set_on_receive(self.preProcessOnReceive)
            self.connector.start()

    def setOnReceive(self, fn):
        self.onReceive = fn

    async def getStates(self):
        try:
            t1 = self.holdAndWaitLoop.create_task(self.copter.telemetry.position().__anext__())
            t2 = self.holdAndWaitLoop.create_task(self.copter.telemetry.battery().__anext__())
            t3 = self.holdAndWaitLoop.create_task(self.copter.telemetry.attitude_quaternion().__anext__())
            t4 = self.holdAndWaitLoop.create_task(self.copter.telemetry.armed().__anext__())
            t5 = self.holdAndWaitLoop.create_task(self.copter.telemetry.landed_state().__anext__())

            await asyncio.wait([t1, t2, t3, t4, t5])
            q = t3.result()
            self.stateMatrix.state.armed = t4.result()
            self.stateMatrix.state.position = t1.result()
            self.stateMatrix.state.landed_state = t5.result()

            roll, pitch, heading = quaternion_to_euler_angle_vectorized(q.w, q.x, q.y, q.z)
            self.stateMatrix.state.heading = heading

            # self.connector.sendMessage(message="OPERATION", status="SYNC", metadata={
            #     "armed": self.state.armed,
            #     "heading": self.state.heading,
            #     "gps": {
            #         "lat": position.latitude_deg,
            #         "lng": position.longitude_deg,
            #         "alt": position.absolute_altitude_m
            #     }
            # })
        except Exception as ex:
            print("ERROR", ex)

    def run(self) -> None:
        lastChecked = time.time()
        while True:
            start = time.time()

            if self.fn is None or (time.time() - lastChecked) > 0.1:
                self.holdAndWaitLoop.run_until_complete(self.getStates())
                lastChecked = time.time()

            if self.fn is not None:
                self.currentState = not self.fn.wait(self.stateMatrix.state)

            if self.currentState == False:
                self.currentId, self.fn = self.stateMatrix.getAsync()

                if (self.currentTask is None or self.currentTask.done() or self.currentTask.cancelled()) \
                        and self.fn is not None:
                    self.currentTask = self.holdAndWaitLoop.create_task(self.fn.fn(*self.fn.l, **self.fn.dc))
                    if(type(self.fn.wait(self.stateMatrix.state)) is not type(True)):
                        self.fn.wait = self.fn.wait(self.stateMatrix.state)

                    print("CREATING NEW TASK!!!")

            print(self.stateMatrix.holds.qsize(), self.currentId, self.currentState)

            diff = time.time() - start
            time.sleep(1.2 - diff)

    def preProcessOnReceive(self, msg):
        print("MESSAGE", msg)
        if(msg['status'] == "COPTER_OPERATION"):
            if(msg['message'] == DroneOperations.START_MISSION.name):
                self.runMission()

            if(msg['message'] == DroneOperations.SYNC_MISSION.name):
                mission_id = msg['syncData']['id']
                print(mission_id)

        if(self.onReceive is not None):
            self.onReceive(msg)

    def getDistance(self, targetLocation):
        position1 = self.stateMatrix.state.position
        distance = get_distance_metres(IORPosition(position1), targetLocation)
        return distance

    def followPath(self, lat, lng):
        bearing = get_bearing(IORPosition(self.stateMatrix.state.position), IORPosition(lat=lat,lng=lng))
        self.holdAndWait(
            self.copter.action.goto_location,
            lambda state: self.getDistance(IORPosition(lat=lat, lng=lng)) > 3,
            lat, lng, 500, bearing
        )

    def setAltitude(self, targetAltitude):
        id = self.holdAndWait(self.copter.action.set_takeoff_altitude, lambda state: wait(2), targetAltitude)
        print("TAKEOFF ALTITUDE", id)

    def takeoff(self, targetAltitude=5):
        self.setAltitude(targetAltitude)
        id = self.holdAndWait(
            self.copter.action.takeoff,
            lambda state: state.altitude() > targetAltitude * 0.95
        )
        print("TAKEOFF", id)

    def land(self):
        self.holdAndWait(self.copter.action.land,
                         lambda state: state.landed_state == LandedState.LANDING
                )

    def holdAndWait(self, future, wait, *tp, **dt):
        if wait is None:
            wait = lambda state: True
        return self.stateMatrix.pushAsyncMethod(IOTFunctionUtils(future, wait,*tp,**dt))

    def arm(self):
        id = self.holdAndWait(self.copter.action.arm, lambda state: state.armed)
        print("arming", id)

    def disarm(self):
        print("disarming")
        self.holdAndWait(self.copter.action.disarm, lambda state: not state.armed)

    def runMission(self):
        print("Running Mission")
        self.arm()
        self.takeoff(10)
        mission = self.httpClient.downloadMission()
        waypoints = mission['waypoints']
        print(waypoints)
        for waypoint in waypoints:
            print("Waypoint Start", waypoint)
            self.followPath(waypoint['latlng']['lat'], waypoint['latlng']['lng'])
            print("Waypoint Ended", waypoint)

def on_receive(msg):
    print(msg)

# async def run():
#     drone = System()
#     await drone.connect()
#     print("Connected")
#
#
#
#     ior_drone = IOTClientWrapper(token=token, config=configFrom)
#     ior_drone.set_on_receive(on_receive)
#     ior_drone.start()
#
#     while True:
#         position = await drone.telemetry.position().__anext__()
#         velocity = await drone.telemetry.velocity_ned().__anext__()
#         data = {
#             "armed": await drone.telemetry.armed().__anext__(),
#             "gps": {
#                 "lat": position.latitude_deg,
#                 "lng": position.longitude_deg,
#                 "alt": position.absolute_altitude_m
#             },
#             "battery": (await drone.telemetry.battery().__anext__()).voltage_v,
#             "flight_mode": (await drone.telemetry.flight_mode().__anext__()).name,
#             "velocity": {
#                 "north": velocity.north_m_s,
#                 "east": velocity.east_m_s,
#                 "down": velocity.down_m_s
#             }
#         }
#
#         print(data)
#         ior_drone.sendMessage(message ="Test", metadata=data, status="SYNC_RECEIVER")
#         await asyncio.sleep(3)

config = {
    "server": "localhost",
    "httpPort": 5001,
    "tcpPort": 8000,
}

configFrom = config.copy()
configFrom['file'] = "C:\\Users\\Asus\\Downloads\\60033040e64ada000177f6ee0.json"
token = "default"

if __name__ == "__main__":
    droneHttpClient = DroneHttpClient()
    droneHttpClient.fetchToken("admin", "admin")
    ior_connector = IOTClientWrapper(token=token, config=configFrom)
    drone = System()
    iorDrone = MavDrone(drone, connector=ior_connector, httpClient=droneHttpClient)
    iorDrone.arm()
    iorDrone.takeoff(10)
    iorDrone.land()