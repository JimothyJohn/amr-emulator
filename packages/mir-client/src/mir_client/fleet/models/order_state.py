from enum import StrEnum


class OrderState(StrEnum):
    ABORTED = "Aborted"
    ABORTING = "Aborting"
    CREATED = "Created"
    EXECUTING = "Executing"
    FINISHED = "Finished"
    OUTBOUND = "Outbound"
    PAUSED = "Paused"
    PENDING = "Pending"
    UPDATED = "Updated"
    WAITINGFORINPUT = "WaitingForInput"

    def __str__(self) -> str:
        return str(self.value)
