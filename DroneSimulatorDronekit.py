import dronekit, time

from ior_research import IOTClient, IOTClientWrapper
from queue import Queue
from threading import Thread
import threading
import math
import ctypes


HOST = "127.0.0.1"
data = Queue()


def copterManager():
    missions = Queue()
    try:
        while True:
            if data.empty():
                time.sleep(0.5)
                continue
            
            command = data.get()
            print("COMMAND",command)
            if(command['status'] == "MISSIONS"):
                missions.put(command['syncData']['waypoints'])
            elif(command['status'] == "START"):
                waypoints = missions.get()
                print("waypoints",waypoints)
                copter.armed = True
                copter.mode = "GUIDED"

                while not copter.armed:
                    print(" Waiting for arming...")
                    time.sleep(1)

                targetAltitude = 10
                copter.simple_takeoff(targetAltitude)
                while True:
                    print(" Altitude: ", copter.location.global_relative_frame.alt)
                    # Break and return from function just below target altitude.
                    if copter.location.global_relative_frame.alt >= targetAltitude * 0.95:
                        print("Reached target altitude")
                        break
                    time.sleep(1)
                for waypoint in waypoints:
                    point = dronekit.LocationGlobalRelative(waypoint['latitude'],waypoint['longitude'],targetAltitude)
                    distance_to_waypoint = get_distance_metres(copter.location.global_relative_frame,point)
                    distance_to_waypoints = np.zeros(shape=(10,))
                    counter = 0
                    while distance_to_waypoint > 0.5 and abs(distance_to_waypoints.mean() - distance_to_waypoint) > 0.05:
                        copter.simple_goto(point)
                        distance_to_waypoint = get_distance_metres(copter.location.global_relative_frame, point)
                        distance_to_waypoints[counter] = distance_to_waypoint


                        counter += 1
                        if counter == distance_to_waypoints.shape[0]:
                            counter = 0

                        time.sleep(0.5)

                copter.mode = dronekit.VehicleMode("LAND")
                print("Mission Completed")
    finally:
        print("Mission Terminated")

def detectLocationChanges(current:dronekit.LocationGlobal,previous:dronekit.LocationGlobal):
    location = previous
    flag = False

    if(previous.lat != current.lat):
        location.lat = current.lat
        flag = True
    if(previous.lon != current.lon):
        location.lon = current.lon
        flag = True

    if flag:
        return location
    else:
        return None

previous_location = None

def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def get_id(self):
    if hasattr(self, '_thread_id'):
        return self._thread_id
    for id, thread in threading._active.items():
        if thread is self:
            return id

def on_receive(x):
    global manager
    print("Received", x)
    if 'status' in x:
        if x['status'] == "ERROR":
            print("Mission Terminate Command Receive")
            raise_exception(manager)
            while not data.empty():
                data.get_nowait()
            copter.mode = dronekit.VehicleMode("RTL")
            manager = Thread(target=copterManager)
            manager.start()

    data.put(x)
    print("Data Queue: ",data)


def raise_exception(self):
    thread_id = get_id(self)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                     ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        print('Exception raise failure')

from ior_research.drone.ior_drone import Drone, get_location_from_distance, createCircle

copter = dronekit.connect("127.0.0.1:14551", wait_ready=True)

def location_callback(self, attr_name, value: dronekit.LocationGlobal):
    global previous_location
    if previous_location is None:
        previous_location = value
    callback  = detectLocationChanges(current=value,previous=previous_location)
    if callback is not None:
        metadata = {"armed": copter.armed, "lat": copter.location.global_relative_frame.lat,
                       "lng": copter.location.global_relative_frame.lon, "alt": copter.location.global_relative_frame.alt}
        print(metadata)
        #ior_drone.client.sendMessage("", metadata=metadata, status="SYNC_RECEIVER")
    previous_location = value

copter.location.add_attribute_listener('global_frame', location_callback)


drone = Drone(copter)
copter.mode = "GUIDED"
drone.arm()
drone.takeoff(10)
drone.setHeading(45)

copter.mode = "LAND"
time.sleep(10)

while True:
    pass

time.sleep(5)

config = {
        "server": "localhost",
        "httpPort": 5001,
        "tcpPort": 8000,
    }

configFrom = config.copy()
configFrom['file'] = "C:\\Users\\Asus\\Downloads\\5ffb51e82ab79c0001510fa20.json"
token = "32dd720b-e43a-4750-a786-059ac5a2aa55"

ior_drone = IOTClientWrapper(token=token,config=configFrom)
ior_drone.set_on_receive(on_receive)
ior_drone.start()

manager = Thread(target=copterManager)
manager.start()
manager.join()

copter.airspeed = 3

targetAltitude = 10
drone = Drone(copter)
time.sleep(2)
drone.takeoff(targetAltitude)
drone.setHeading(45)
target_location = get_location_from_distance(drone.copter.heading,drone.copter.location.global_relative_frame,100)
points = createCircle(drone.copter.location.global_relative_frame,50)

for target_location in points:
    drone.copter.simple_goto(target_location)
    time.sleep(10)

drone.changeMode('RTL')

time.sleep(15)

copter.armed = False
copter.close()

ior_drone.terminate()
exit(0)