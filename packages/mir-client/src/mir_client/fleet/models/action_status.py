from enum import StrEnum


class ActionStatus(StrEnum):
    ABORTED = "Aborted"
    EXECUTING = "Executing"
    FAILED = "Failed"
    INVALID = "Invalid"
    SUCCEEDED = "Succeeded"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
