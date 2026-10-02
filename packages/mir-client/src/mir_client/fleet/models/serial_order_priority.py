from enum import StrEnum


class SerialOrderPriority(StrEnum):
    HIGH = "High"
    LOW = "Low"
    MEDIUM = "Medium"

    def __str__(self) -> str:
        return str(self.value)
