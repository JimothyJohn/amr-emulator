from enum import StrEnum


class MarkerType1(StrEnum):
    BAR = "Bar"
    L = "L"
    PALLETRACK = "PalletRack"
    STRIPE = "Stripe"
    V = "V"
    VL = "VL"

    def __str__(self) -> str:
        return str(self.value)
