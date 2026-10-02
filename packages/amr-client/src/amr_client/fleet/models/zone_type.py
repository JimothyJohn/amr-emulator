from enum import StrEnum


class ZoneType(StrEnum):
    ACCESSZONE = "AccessZone"
    DIRECTIONALZONE = "DirectionalZone"
    EVACUATIONZONE = "EvacuationZone"
    FLOORZONE = "FloorZone"
    FORBIDDENZONE = "ForbiddenZone"
    INTEGRATIONZONE = "IntegrationZone"
    LIMITZONE = "LimitZone"
    LOCKZONE = "LockZone"
    PLANNERZONE = "PlannerZone"
    PREFERREDZONE = "PreferredZone"
    SOUNDANDLIGHTZONE = "SoundAndLightZone"
    SPEEDZONE = "SpeedZone"
    UNPREFERREDZONE = "UnpreferredZone"
    WALLZONE = "WallZone"

    def __str__(self) -> str:
        return str(self.value)
