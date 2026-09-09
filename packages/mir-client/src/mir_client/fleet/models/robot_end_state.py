from enum import StrEnum


class RobotEndState(StrEnum):
    BRAKE_RELEASED = "Brake Released"
    CABLE_CHARGER_CONNECTED = "Cable Charger Connected"
    EMERGENCY_STOP = "Emergency Stop"
    ERROR = "Error"
    IDLE = "Idle"
    KEY_STATE_IDLE = "Key State: Idle"
    KEY_STATE_MANUAL = "Key State: Manual"
    MANUAL_CONTROL = "Manual Control"
    OPERATIONAL = "Operational"
    PAUSED = "Paused"
    PROTECTIVE_STOP = "Protective Stop"
    RESET_REQUIRED = "Reset Required"
    SHUTTING_DOWN = "Shutting Down"
    STARTING = "Starting"

    def __str__(self) -> str:
        return str(self.value)
