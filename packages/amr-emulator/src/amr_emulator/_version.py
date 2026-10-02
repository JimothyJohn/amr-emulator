# Rewritten by scripts/build_versioned.py at release time so that the package
# version matches the MiR software version it emulates by default
# (e.g. amr-emulator==3.5.4 defaults to the 3.5.4 spec).
__version__ = "0.0.0.dev0"

# None means "newest version in the bundled registry".
DEFAULT_MIR_VERSION: str | None = None
