from enum import StrEnum


class DockingType(StrEnum):
    BAR = "Bar"
    LEG = "Leg"

    def __str__(self) -> str:
        return str(self.value)
