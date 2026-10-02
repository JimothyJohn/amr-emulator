from enum import StrEnum


class SiteActionType(StrEnum):
    CREATE = "Create"
    DELETE = "Delete"
    LOCKSTATECHANGE = "LockStateChange"
    NONE = "None"
    UPDATE = "Update"

    def __str__(self) -> str:
        return str(self.value)
