from enum import StrEnum


class OrderPriority(StrEnum):
    HIGH = "High"
    LOW = "Low"
    MEDIUM = "Medium"

    def __str__(self) -> str:
        return str(self.value)
