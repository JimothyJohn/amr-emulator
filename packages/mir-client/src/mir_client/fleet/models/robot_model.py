from enum import StrEnum


class RobotModel(StrEnum):
    MIR100 = "Mir100"
    MIR1000 = "Mir1000"
    MIR1200PALLETJACK = "Mir1200PalletJack"
    MIR1350 = "Mir1350"
    MIR200 = "Mir200"
    MIR250 = "Mir250"
    MIR500 = "Mir500"
    MIR600 = "Mir600"

    def __str__(self) -> str:
        return str(self.value)
