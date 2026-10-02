from enum import StrEnum


class GripperState(StrEnum):
    CLOSED = "Closed"
    CLOSING = "Closing"
    ERROR = "Error"
    HOMING = "Homing"
    OPEN = "Open"
    OPENING = "Opening"

    def __str__(self) -> str:
        return str(self.value)
