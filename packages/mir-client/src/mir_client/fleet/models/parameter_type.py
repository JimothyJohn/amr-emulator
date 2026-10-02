from enum import StrEnum


class ParameterType(StrEnum):
    BOOLEAN = "Boolean"
    CART = "Cart"
    DURATION = "Duration"
    FLOAT = "Float"
    FOOTPRINT = "Footprint"
    INTEGER = "Integer"
    IOMODULE = "IoModule"
    JSON = "Json"
    LIST = "List"
    MARKERTYPE = "MarkerType"
    POSITION = "Position"
    ROLE = "Role"
    SELECTION = "Selection"
    SOUND = "Sound"
    STATICINTEGER = "StaticInteger"
    STRING = "String"

    def __str__(self) -> str:
        return str(self.value)
