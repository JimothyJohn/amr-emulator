from enum import StrEnum


class LockZoneState(StrEnum):
    LOCKED = "Locked"
    LOCKING = "Locking"
    UNLOCKED = "Unlocked"

    def __str__(self) -> str:
        return str(self.value)
