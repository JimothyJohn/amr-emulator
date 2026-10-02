from enum import StrEnum


class TopModuleEventType(StrEnum):
    ERROR = "Error"
    EVENT = "Event"

    def __str__(self) -> str:
        return str(self.value)
