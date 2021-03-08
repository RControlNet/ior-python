import time, math, enum
from pymavlink import mavutil
import numpy as np
from ior_research.utils.httpclients import IORHttpClient
import requests
from ior_research.IOTClient import IOTClientWrapper
from dronekit import Vehicle, Battery, LocationLocal, LocationGlobal, LocationGlobalRelative, GPSInfo
from ior_research.utils.consts import DroneAttributes, DroneOperations, MessageStatus, DroneActions, MissionStatus
from ior_research.utils.video import VideoTransmitter, createVideoTransmitter
from ior_research.utils import loadConfig
import threading

class DroneHttpClient(IORHttpClient):
    def __init__(self, server=None):
        IORHttpClient.__init__(self, server)

    def downloadMission(self):
        response = requests.get(self.server + "/drone/mission", headers={
            "Authorization": "Bearer " + self.token
        }, verify=self.verify)
        return response.json()

class DroneState:
    def __init__(self):
        self.armed = False
        self.heading = 0.0
        self.battery: Battery = 0
        self.position= None
        self.gs = 0

    def compute(self):
        metadata = {
            "lat": self.position.lat,
            "lng": self.position.lon,
            "alt": self.position.alt,
        }
        return metadata

    def calculate(self,n):
        min = n * 3.7
        max = n * 4.2

        return (self.battery-min) * 100/(max-min)

    def altitude(self):
        return self.position.relative_altitude_m

    def absoluteAltitude(self):
        return self.position.absolute_altitude_m

class IORPosition:
    def __init__(self, position= None, lat = None, lng=None):
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

class IOTFunctionUtils:
    def __init__(self, fn, wait, *l, **dc):
        self.fn = fn
        self.l = l
        self.dc = dc
        self.wait = wait

def map_name_drone_attribute(name, attribute: enum.Enum):
    return name == attribute.name

class Mission:
    def __init__(self, waypoints):
        self.task = None
        self.runnerState = True
        self.waypointIndex = -1
        self.actionIndex = 0
        self.missionStatus = MissionStatus.NONE
        self.setWaypoints(waypoints)

    def setWaypoints(self, waypoints):
        assert self.missionStatus != MissionStatus.ON_MISSION, "Cannot set Waypoint when on waypoint"
        self.waypoints = waypoints
        self.missionStatus = MissionStatus.MISSION_SYNCED
        self.waypointIndex = -1
        self.actionIndex = 0

    def terminateMission(self, state = False):
        self.runnerState = state
        if(state == False):
            self.missionStatus = MissionStatus.MISSION_TERMINATED

    def getMissionState(self):
        if self.waypointIndex == -1:
            return None
        return {
            "missionStatus": self.missionStatus.name,
            "waypointId": self.waypoints[self.waypointIndex]['id']
        }

    def executeMission(self, mav):
        if self.task is not None or len(self.waypoints) < 1:
            print("ERROR EXECUTING MISSION")
            return
        mav.changeMode("GUIDED")
        mav.arm()
        mav.takeoff(1)()
        self.runnerState = True
        print("RUNNING MISSION")
        def threadRunner():
            self.missionStatus = MissionStatus.ON_MISSION
            while self.runnerState and self.waypointIndex < len(self.waypoints):
                print("Running Thread")
                if self.waypointIndex == -1:
                    checker = lambda: mav.copter.mode.name == 'GUIDED' and mav.copter.location.global_relative_frame.alt >= mav.targetAltitude * 0.95
                else:
                    waypoint = self.waypoints[self.waypointIndex]
                    actions = [waypoint['action']]
                    latlng = waypoint['latlng']
                    checker = mav.goToWaypoint(lat=latlng['lat'], lng=latlng['lng'])

                state = checker()
                if state and self.waypointIndex != -1:
                    actionChecker = lambda: True
                    if self.actionIndex < len(actions):
                        action = actions[self.actionIndex]
                        print(action)
                        action_name = action['actionName']
                        action_value = action['actionValue']

                        if map_name_drone_attribute(action_name, DroneActions.SET_ALTITUDE):
                            mav.takeoff(int(action_value))
                            actionChecker = lambda: (mav.copter.location.global_relative_frame.alt >= mav.targetAltitude * 0.95 and mav.copter.location.global_relative_frame.alt <= mav.targetAltitude * 1.2)


                    actionCompleted = actionChecker()
                    if actionCompleted:
                        self.actionIndex += 1
                    print("Action",actionCompleted, self.actionIndex)
                    state = state and actionCompleted and not (self.actionIndex < len(actions))

                if state:
                    self.waypointIndex += 1
                    self.actionIndex = 0

                print(state, self.waypointIndex)
                time.sleep(5)

            self.terminateMission()
            self.missionStatus = MissionStatus.MISSION_COMPLETED
            self.waypointIndex = -1
            self.actionIndex = 0
            mav.onMissionComplete(mav)

        taskThread = threading.Thread(target=threadRunner)
        taskThread.start()



class Drone:
    def __init__(self, copter: Vehicle, initialMode = "GUIDED"):
        self.copter = copter
        # while not self.copter.is_armable:
        #     print(" Waiting for vehicle to initialise...")
        #     time.sleep(1)
        self.__state = DroneState()
        self.changeMode(initialMode)
        self.copter.add_attribute_listener("*", self.__callback_changes)
        self.targetAltitude = self.copter.location.global_relative_frame.alt
        self.videoTransmitter: VideoTransmitter = None

        data = loadConfig()
        videoConfig = data['video']
        self.transmitVideo = ('transmit' in videoConfig and videoConfig['transmit'] == 'true')
        self.droneHttpClient = DroneHttpClient()
        self.droneHttpClient.fetchToken(data['username'], data['password'])
        self.mission = Mission([])
        self.onMissionComplete = lambda mav: mav.changeMode("RTL")

    def setOnCompleteMission(self, on_complete):
        self.onMissionComplete = on_complete

    def preProcessMessage(self, msg, callback=None):
        print("Preprocess Message", msg)
        if 'message' in msg:
            message = msg['message']
            status = None
            if 'status' in msg:
                status = msg['status']

            if map_name_drone_attribute(message, DroneOperations.START_STREAMER):
                if(self.transmitVideo):
                    if self.videoTransmitter is None:
                        self.videoTransmitter = createVideoTransmitter()

                    if not self.videoTransmitter.checkBrowserAlive():
                        self.videoTransmitter.openBrowserAndHitLink()
                    else:
                        self.videoTransmitter.close()
                        self.videoTransmitter = createVideoTransmitter()
                        self.videoTransmitter.openBrowserAndHitLink()

            elif map_name_drone_attribute(message, DroneOperations.SYNC_MISSION) and map_name_drone_attribute(status, MessageStatus.COPTER_OPERATION):
                mission = self.droneHttpClient.downloadMission()
                print(mission)
                self.mission.setWaypoints(mission['waypoints'])
                self.mission.executeMission(self)

            elif map_name_drone_attribute(message, DroneOperations.START_MISSION) and map_name_drone_attribute(status, MessageStatus.COPTER_OPERATION):
                self.mission.terminateMission()

        if callback is not None:
            callback(msg)

    def setClientWrapper(self,wrapper: IOTClientWrapper):
        self.wrapper = wrapper
        fn = self.wrapper.fn
        self.wrapper.set_on_receive(lambda msg: self.preProcessMessage(msg, fn))

    def getState(self):
        return self.__state

    def __callback_changes(self, vechile, attr_name, value):
        attr_name = attr_name.upper()
        attr_name = attr_name.replace(".", "__")

        if map_name_drone_attribute(attr_name, DroneAttributes.LAST_HEARTBEAT):
            return None

        if map_name_drone_attribute(attr_name,DroneAttributes.HEADING):
            self.__state.heading = value
        elif map_name_drone_attribute(attr_name, DroneAttributes.BATTERY):
            self.__state.battery = value.__dict__
        elif map_name_drone_attribute(attr_name, DroneAttributes.GROUNDSPEED):
            self.__state.gs = value
        elif map_name_drone_attribute(attr_name, DroneAttributes.LOCATION__GLOBAL_RELATIVE_FRAME):
            self.__state.position = value.__dict__
        elif map_name_drone_attribute(attr_name, DroneAttributes.ARMED):
            self.__state.armed = value
        # else:
        #     print("Attribute Change", attr_name ,value)

    def arm(self, state = True):
        while self.copter.armed != state:
            time.sleep(1)
            self.copter.armed = state
            print("Waiting for arm", self.copter.armed)

    def goToWaypoint(self, lat, lng):
        point = LocationGlobalRelative(lat, lng, self.targetAltitude)
        position = IORPosition(lat=lat, lng=lng)
        self.copter.simple_goto(point)

        def wait():
            point2 = self.copter.location.global_relative_frame
            position2 = IORPosition(lat=point2.lat, lng = point2.lon)
            distance = get_distance_metres(position, position2)
            print(distance)
            return  distance < 1

        return wait

    def setTargetAltitude(self,altitude):
        self.targetAltitude = altitude

    def moveForward(self,distance=0,altitude=None):
        if altitude is not None:
            self.setTargetAltitude(altitude)

    def changeMode(self,mode):
        self.copter.mode = mode

    def takeoff(self,altitude = 1):
        self.setTargetAltitude(altitude)
        self.copter.simple_takeoff(self.targetAltitude)
        def wait(flag=-1):
            counter = 0
            while self.copter.mode.name == 'GUIDED' and (flag == -1 or counter < flag):
                # Break and return from function just below target altitude.
                if self.copter.location.global_relative_frame.alt is None:
                    continue;
                if self.copter.location.global_relative_frame.alt >= self.targetAltitude * 0.95:
                    print("Reached target altitude")
                    break
                time.sleep(1)

        return wait

    def setHeading(self,heading, flag=-1):
        msg = self.copter.message_factory.command_long_encode(
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
            0,  # confirmation
            heading,  # param 1, yaw in degrees
            0,  # param 2, yaw speed deg/s
            1 if (heading - self.copter.heading) < 0 else 0,  # param 3, direction -1 ccw, 1 cw
            0,  # param 4, relative offset 1, absolute angle 0
            0, 0, 0)  # param 5 ~ 7 not used
        self.copter.send_mavlink(msg)

        msg = self.copter.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target_system, target_component
            mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame
            0b0000111111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions
            0, 0, 0,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        # send command to vehicle
        self.copter.send_mavlink(msg)

        def wait():
            counter = 0
            while self.copter.mode.name == "GUIDED" and abs(heading - self.copter.heading) > 5 and (flag == -1 or counter < flag):
                print(heading - self.copter.heading)
                msg = self.copter.message_factory.command_long_encode(
                    0, 0,  # target system, target component
                    mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
                    0,  # confirmation
                    heading,  # param 1, yaw in degrees
                    0,  # param 2, yaw speed deg/s
                    1 if (heading - self.copter.heading) < 0 else 0,  # param 3, direction -1 ccw, 1 cw
                    0,  # param 4, relative offset 1, absolute angle 0
                    0, 0, 0)  # param 5 ~ 7 not used
                self.copter.send_mavlink(msg)

                msg = self.copter.message_factory.set_position_target_local_ned_encode(
                    0,  # time_boot_ms (not used)
                    0, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame
                    0b0000111111000111,  # type_mask (only speeds enabled)
                    0, 0, 0,  # x, y, z positions
                    0, 0, 0,  # x, y, z velocity in m/s
                    0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
                    0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
                # send command to vehicle
                self.copter.send_mavlink(msg)
                counter += 1
                time.sleep(0.1)
        return wait

def createCircle(center,radius,yaw=0):
    points = []

    target_location = get_location_from_distance(yaw,center,radius)
    points.append(target_location)
    c_yaw = 0
    while c_yaw < 360:
        target_location = get_location_from_distance(c_yaw, center, radius)
        points.append(target_location)
        c_yaw += 30

    return points


def get_location_from_distance(yaw,current_location,target_distance):
    rad = math.radians(yaw)
    dNorth = math.cos(rad) * target_distance
    dEast = math.sin(rad) * target_distance
    return get_location_metres(current_location,dNorth,dEast)

def get_location_metres(original_location, dNorth, dEast):
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lng + (dLon * 180 / math.pi)

    return (newlat,newlon);

def get_distance_metres(aLocation1: IORPosition, aLocation2: IORPosition):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lng - aLocation1.lng
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5

def get_bearing(aLocation1: IORPosition, aLocation2:IORPosition):
    off_x = aLocation2.lng - aLocation1.lng
    off_y = aLocation2.lat - aLocation1.lat
    bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
    if bearing < 0:
        bearing += 360.00
    return bearing;


def quaternion_to_euler_angle_vectorized(w, x, y, z):
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = np.degrees(np.arctan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = np.where(t2>+1.0,+1.0,t2)
    #t2 = +1.0 if t2 > +1.0 else t2

    t2 = np.where(t2<-1.0, -1.0, t2)
    #t2 = -1.0 if t2 < -1.0 else t2
    Y = np.degrees(np.arcsin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = np.degrees(np.arctan2(t3, t4))

    return X, Y, Z