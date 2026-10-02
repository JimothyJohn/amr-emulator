from enum import StrEnum


class BrakeState(StrEnum):
    ACTIVATING = "Activating"
    ACTIVE = "Active"
    DEACTIVATING = "Deactivating"
    ERROR = "Error"
    HOMING = "Homing"
    INACTIVE = "Inactive"
    INITIALIZING = "Initializing"

    def __str__(self) -> str:
        return str(self.value)
