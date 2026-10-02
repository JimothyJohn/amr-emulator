from enum import StrEnum


class PlcAction(StrEnum):
    ADD = "Add"
    NONE = "None"
    SET = "Set"
    SUBTRACT = "Subtract"

    def __str__(self) -> str:
        return str(self.value)
