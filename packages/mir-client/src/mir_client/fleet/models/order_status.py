from enum import StrEnum


class OrderStatus(StrEnum):
    ABORTED = "Aborted"
    ABORTING = "Aborting"
    EXECUTING = "Executing"
    FINISHED = "Finished"
    INVALID = "Invalid"
    OUTBOUND = "Outbound"
    PENDING = "Pending"
    WAITING = "Waiting"

    def __str__(self) -> str:
        return str(self.value)
