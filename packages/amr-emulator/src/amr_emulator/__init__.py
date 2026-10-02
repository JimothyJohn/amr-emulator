"""amr-emulator: local, spec-faithful emulator of the MiR robot REST API."""

from amr_emulator._version import __version__
from amr_emulator.app import create_app
from amr_emulator.registry import supported_versions

__all__ = ["__version__", "create_app", "supported_versions"]
