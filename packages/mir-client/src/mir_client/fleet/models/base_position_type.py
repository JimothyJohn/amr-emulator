from enum import StrEnum


class BasePositionType(StrEnum):
    EVACUATION = "Evacuation"
    ROBOT = "Robot"
    STAGING = "Staging"

    def __str__(self) -> str:
        return str(self.value)
