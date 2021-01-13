import time, math
from dronekit import LocationGlobal, LocationGlobalRelative, VehicleMode
from pymavlink import mavutil

class Drone:
    def __init__(self, copter):
        self.copter = copter
        while not self.copter.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)
        self.targetAltitude = self.copter.location.global_relative_frame.alt
        self.changeMode('GUIDED')


    def arm(self, state = True):
        while self.copter.armed != state:
            time.sleep(1)
            self.copter.armed = state
            print("Waiting for arm", self.copter.armed)

    def setTargetAltitude(self,altitude):
        self.targetAltitude = altitude

    def moveForward(self,distance=0,altitude=None):
        if altitude is not None:
            self.setTargetAltitude(altitude)

    def changeMode(self,mode):
        self.copter.mode = VehicleMode(mode)

    def takeoff(self,altitude = 1):
        self.setTargetAltitude(altitude)
        self.copter.simple_takeoff(self.targetAltitude)
        while self.copter.mode.name == 'GUIDED':
            print(" Altitude: ", self.copter.location.global_relative_frame)
            # Break and return from function just below target altitude.
            if self.copter.location.global_relative_frame.alt is None:
                continue;
            if self.copter.location.global_relative_frame.alt >= self.targetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)

    def setHeading(self,heading):
        while self.copter.mode.name == "GUIDED" and abs(heading - self.copter.heading) > 5:
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

            time.sleep(0.1)

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
    dNorth =  math.cos(rad) * target_distance
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


def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lng - aLocation1.lng
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5


def get_bearing(aLocation1, aLocation2):
    off_x = aLocation2.lon - aLocation1.lon
    off_y = aLocation2.lat - aLocation1.lat
    bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
    if bearing < 0:
        bearing += 360.00
    return bearing;