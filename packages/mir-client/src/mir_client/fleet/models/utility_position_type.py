from enum import StrEnum


class UtilityPositionType(StrEnum):
    CART = "Cart"
    DEEPLANE = "DeepLane"
    ELEVATEDBARPALLET = "ElevatedBarPallet"
    ELEVATEDFIDUCIALPALLET = "ElevatedFiducialPallet"
    ELEVATEDLPALLET = "ElevatedLPallet"
    ELEVATEDPALLETPALLET = "ElevatedPalletPallet"
    ELEVATEDPALLETRACK = "ElevatedPalletRack"
    ELEVATEDSTRIPEPALLET = "ElevatedStripePallet"
    ELEVATEDVLPALLET = "ElevatedVlPallet"
    PALLETFLOOR = "PalletFloor"
    SHELF = "Shelf"

    def __str__(self) -> str:
        return str(self.value)
