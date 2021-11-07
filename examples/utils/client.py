from dronekit import VehicleMode, LocationGlobalRelative
import dronekit
import time
import math

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
