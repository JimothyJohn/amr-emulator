from enum import StrEnum


class ObstacleHistoryClearing(StrEnum):
    CLEARALL = "ClearAll"
    CLEARINFRONTOFROBOT = "ClearInFrontOfRobot"
    NOCLEARING = "NoClearing"

    def __str__(self) -> str:
        return str(self.value)
