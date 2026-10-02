from enum import StrEnum


class SiteEntityType(StrEnum):
    CART = "Cart"
    FOOTPRINT = "Footprint"
    GROUP = "Group"
    IOMODULE = "IoModule"
    MAP = "Map"
    MARKERTYPE = "MarkerType"
    MISSION = "Mission"
    MISSIONGROUP = "MissionGroup"
    POSITION = "Position"
    SOUND = "Sound"
    ZONE = "Zone"

    def __str__(self) -> str:
        return str(self.value)
