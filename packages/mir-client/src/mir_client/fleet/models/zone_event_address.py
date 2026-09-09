from enum import StrEnum


class ZoneEventAddress(StrEnum):
    INTEGRATION = "Integration"
    TOPMODULE = "TopModule"

    def __str__(self) -> str:
        return str(self.value)
