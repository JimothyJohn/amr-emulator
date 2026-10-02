from enum import StrEnum


class ZoneEventType(StrEnum):
    ENTRY = "Entry"
    EXIT = "Exit"

    def __str__(self) -> str:
        return str(self.value)
