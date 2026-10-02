from enum import StrEnum


class HeightState(StrEnum):
    CHANGING = "Changing"
    ERROR = "Error"
    HOMING = "Homing"
    IDLE = "Idle"

    def __str__(self) -> str:
        return str(self.value)
