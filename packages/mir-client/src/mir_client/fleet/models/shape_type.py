from enum import StrEnum


class ShapeType(StrEnum):
    LINE = "Line"
    POLYGON = "Polygon"

    def __str__(self) -> str:
        return str(self.value)
