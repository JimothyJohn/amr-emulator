from enum import StrEnum


class RequestedRobotEndState(StrEnum):
    OPERATIONAL = "Operational"
    PAUSED = "Paused"

    def __str__(self) -> str:
        return str(self.value)
