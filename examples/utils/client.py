from dronekit import VehicleMode, LocationGlobalRelative
import dronekit
import time
import math

from pymavlink import  mavutil
from ior_research.drone.ior_drone import get_location_from_distance, IORPosition, get_distance_metres

ALTITUDE = 1

def calculateLatLng(current_location, velocity, heading):
    distance = velocity + 0.5
    if abs(velocity) < 0.2:
        distance = 0
    (lat, lng) = get_location_from_distance(heading, current_location, distance)
    return (lat, lng)

def calculateYaw(velocity_y, velocity_x):
    calculated_yaw = 90 + math.degrees(math.atan2(-velocity_y, velocity_x))
    return calculated_yaw

def increseAltitude(factor):
    global ALTITUDE
    ALTITUDE += factor

def setHeading(vehicle, heading):
    msg = vehicle.message_factory.command_long_encode(
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
        0,  # confirmation
        vehicle.heading + heading,  # param 1, yaw in degrees
        0,  # param 2, yaw speed deg/s
        1 if (heading - vehicle.heading) < 0 else 0,  # param 3, direction -1 ccw, 1 cw
        0,  # param 4, relative offset 1, absolute angle 0
        0, 0, 0)  # param 5 ~ 7 not used
    vehicle.send_mavlink(msg)

    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,  # time_boot_ms (not used)
        0, 0,  # target_system, target_component
        mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0, 0, 0,  # x, y, z positions
        0, 0, 0,  # x, y, z velocity in m/s
        0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle
    vehicle.send_mavlink(msg)

def moveWithVelocity(vehicle, velocity_y, velocity_x):
    desired_yaw = calculateYaw(velocity_y, velocity_x)
    current_yaw = vehicle.heading

    current_location = IORPosition(position=vehicle.location.global_relative_frame)
    speed = max(abs(velocity_y * math.cos(math.radians(desired_yaw))),
                abs(velocity_x * math.sin(math.radians(desired_yaw))))
    vehicle.groundspeed = speed
    (lat,lng) = calculateLatLng(current_location, speed, desired_yaw)
    goto_position = LocationGlobalRelative(lat=lat, lon=lng, alt=ALTITUDE)
    print(desired_yaw, current_yaw, speed, goto_position)
    vehicle.simple_goto(goto_position)


def desiredAltitude(vehicle, value=ALTITUDE):
    vehicle.simple_takeoff(value)
    while vehicle.location.global_relative_frame.alt < value * 0.98:
        print(vehicle.location.global_relative_frame.alt)
        vehicle.simple_takeoff(value)
        time.sleep(1)


def setMode(vehicle, mode):
    vehicle.mode = VehicleMode(mode)
    while vehicle.mode.name != mode:
        print("Waiting for mode to set")
        time.sleep(1)

def connect():
    return dronekit.connect("192.168.66.5:14451", wait_ready=True)

def setup():
    vehicle = connect()
    setMode(vehicle, "GUIDED")
    vehicle.arm(True)
    desiredAltitude(vehicle, ALTITUDE)

    time.sleep(5)

    setMode(vehicle, "LAND")

if __name__ == "__main__":
    setup()
