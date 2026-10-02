from enum import StrEnum


class PalletDockingOption(StrEnum):
    MARKER = "Marker"
    MARKERWITHML = "MarkerWithMl"
    ML = "Ml"

    def __str__(self) -> str:
        return str(self.value)
