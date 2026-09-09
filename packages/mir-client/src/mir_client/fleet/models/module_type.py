from enum import StrEnum


class ModuleType(StrEnum):
    INTERNAL4PORT = "Internal4Port"
    WISE = "Wise"

    def __str__(self) -> str:
        return str(self.value)
