from  mavsdk import System
import asyncio
from ior_research import IOTClient, IOTClientWrapper
from asyncio.events import get_event_loop
import time
from mavsdk.telemetry import LandedState, Position
from ior_research.drone.ior_drone import get_location_from_distance, get_distance_metres
import enum

class DroneOperations(enum.Enum):
    SYNC_MISSION = 1
    START_MISSION = 2

class IORPosition:
    def __init__(self, position: Position = None, lat = None, lng=None):
        if(position is not None):
            self.lat = position.latitude_deg
            self.lng = position.longitude_deg
            self.alt = position.absolute_altitude_m
            self.rAlt = position.relative_altitude_m
        else:
            self.lat = lat
            self.lng = lng
            self.alt = 0
            self.rAlt = 0


    def __toPosition__(self):
        return Position(self.lat, self.lng, self.alt, self.rAlt)
class MavDrone:
    def __init__(self, copter: System, connector: IOTClientWrapper = None):
        self.copter = copter
        self.holdAndWait(self.copter.connect)
        self.onReceive = None
        self.connector = connector
        if(self.connector is not None):
            self.connector.set_on_receive(self.preProcessOnReceive)
            self.connector.start()

    def setOnReceive(self, fn):
        self.onReceive = fn

    def preProcessOnReceive(self, msg):
        print(msg)

    def holdAndWait(self, future, *tp, **dt):
        loop = get_event_loop()
        if type(future) is type(list()) or type(future) is type(tuple()):
            data = []
            for f in future:
                data.append(loop.run_until_complete(f()))
        else:
            data = loop.run_until_complete(future(*tp, **dt))
        return data

    def getStates(self):
        return self.holdAndWait([
            self.copter.telemetry.position().__anext__,
            self.copter.telemetry.armed().__anext__,
            self.copter.telemetry.battery().__anext__
        ])
    def getDistance(self, targetLocation):
        position1 = self.holdAndWait(
            self.copter.telemetry.position().__anext__
        )
        distance = get_distance_metres(IORPosition(position1), targetLocation)
        print(distance)
        return distance

    def followPath(self, lat, lng):
        self.holdAndWait(
            self.copter.action.goto_location,
            lat,
            lng,
            500,
            0
        )

        self.waitTillTrue(lambda: self.getDistance(IORPosition(lat=lat, lng=lng)) > 3)
        self.holdAndWait(self.copter.action.return_to_launch)
        time.sleep(10)

    def takeoff(self, targetAltitude=5):
        self.holdAndWait(self.copter.action.set_takeoff_altitude, targetAltitude)
        self.holdAndWait(
            self.copter.action.takeoff
        )
        self.waitTillTrue(lambda:
            self.holdAndWait(
                self.copter.telemetry.position().__anext__
            ).relative_altitude_m <= targetAltitude * 0.95
        )


    def land(self):
        self.holdAndWait(self.copter.action.land)
        self.waitTillTrue(lambda: self.holdAndWait(self.copter.telemetry.landed_state().__anext__) == LandedState.LANDING )

    def waitTillTrue(self, fn, delay = 0.5):
        flag = True
        while flag:
            flag = fn()
            time.sleep(delay)

    def arm(self):
        print("arming")
        self.holdAndWait(self.copter.action.arm)
        self.waitTillTrue(lambda : not self.holdAndWait(
            self.copter.telemetry.armed().__anext__
        ))

    def disarm(self):
        print("disarming")
        self.holdAndWait(self.copter.action.disarm)

def on_receive(msg):
    print(msg)
#
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
#

config = {
    "server": "localhost",
    "httpPort": 5001,
    "tcpPort": 8000,
}

configFrom = config.copy()
configFrom['file'] = "C:\\Users\\Asus\\Downloads\\5ffb51e82ab79c0001510fa20.json"
token = "default"

if __name__ == "__main__":
    ior_connector = IOTClientWrapper(token=token, config=configFrom)
    drone = System()
    iorDrone = MavDrone(drone, connector=ior_connector)
    while True:
        pass
    position = iorDrone.getStates()[0]
    targetLocation = get_location_from_distance(50, IORPosition(position), 50)
    iorDrone.arm()
    iorDrone.getStates()
    iorDrone.takeoff(5)
    iorDrone.followPath(*targetLocation)

    iorDrone.land()

    # asyncio.run(run())