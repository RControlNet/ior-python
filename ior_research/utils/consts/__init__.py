import enum
import json


class DroneAttributes(enum.Enum):
    GROUNDSPEED = 1
    AIRSPEED = 2
    BATTERY = 3
    HOME_LOCATION = 4
    HEADING = 5
    VELOCITY = 6
    LOCATION__GLOBAL_RELATIVE_FRAME = 7
    LAST_HEARTBEAT = 8
    ARMED = 9
    LOCATION__LOCAL_FRAME = 10

class MissionStatus(enum.Enum):
    MISSION_SYNCED=1
    MISSION_COMPLETED=2
    ON_MISSION=3
    MISSION_TERMINATED=4
    NONE=5

class DroneOperations(enum.Enum):
    SYNC_MISSION = 1
    START_MISSION = 2
    START_STREAMER = 3
    STOP_STREAMER = 4

class DroneActions(enum.Enum):
    SET_ALTITUDE = 1
    SET_HEADING = 2
    DIGITAL_WRITE = 3

class MessageStatus(enum.Enum):
    Initialized=1
    Connected=2
    Disconnected=3
    ERROR=4
    Operation=5
    SYNC=6
    COPTER_OPERATION=7
    MISSION_STATUS=8

class ControlNetConfigs:
    def __init__(self):
        self.token = None

    def toFile(self, path):
        with open(path, "w") as file:
            data = json.dumps(self.__dict__)
            file.write(data)

    def fromFile(self, path):
        with open(path, "r") as file:
            data = file.read()
            obj = json.loads(data)
            self.token = obj['token']