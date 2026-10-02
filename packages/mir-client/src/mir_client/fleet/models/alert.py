from enum import StrEnum


class Alert(StrEnum):
    DEADLOCKDETECTED = "DeadlockDetected"
    INCOMPATIBLEROBOT = "IncompatibleRobot"
    INTERNALALERTREPORTED = "InternalAlertReported"
    INVALIDSITEENTITY = "InvalidSiteEntity"
    PATHCONFLICT = "PathConflict"
    ROBOTERROR = "RobotError"
    ROBOTESTOP = "RobotEstop"

    def __str__(self) -> str:
        return str(self.value)
