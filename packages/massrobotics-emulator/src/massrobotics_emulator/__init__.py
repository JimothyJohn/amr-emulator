"""MassRobotics AMR Interop Standard emulator — Vecna-class robots + receiver."""

from ._version import __version__
from .receiver import InteropReceiver, RobotRecord
from .robot import VECNA_MODELS, AMRConfig, MassRoboticsAMR, vecna_config
from .validation import ProtocolViolation, validation_errors

__all__ = [
    "VECNA_MODELS",
    "AMRConfig",
    "InteropReceiver",
    "MassRoboticsAMR",
    "ProtocolViolation",
    "RobotRecord",
    "__version__",
    "validation_errors",
    "vecna_config",
]
