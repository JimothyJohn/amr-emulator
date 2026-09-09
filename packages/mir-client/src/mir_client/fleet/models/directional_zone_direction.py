from enum import StrEnum


class DirectionalZoneDirection(StrEnum):
    DIRECTION0 = "Direction0"
    DIRECTION135 = "Direction135"
    DIRECTION180 = "Direction180"
    DIRECTION225 = "Direction225"
    DIRECTION270 = "Direction270"
    DIRECTION315 = "Direction315"
    DIRECTION45 = "Direction45"
    DIRECTION90 = "Direction90"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
