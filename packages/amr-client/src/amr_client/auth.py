"""MiR auth helpers for the generated clients.

The robot expects ``Authorization: Basic BASE64(user ":" SHA-256-hex(password))``
(the factory default account is distributor/distributor); MiR Fleet Enterprise
expects an ``x-api-key`` header. Deliberately self-contained — the client must
not depend on the emulator package.
"""

from __future__ import annotations

import base64
import hashlib

DEFAULT_USERNAME = "distributor"
DEFAULT_PASSWORD = "distributor"  # noqa: S105 - MiR's documented factory default


def robot_token(username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> str:
    """The value for the robot's Authorization header, without the scheme."""
    digest = hashlib.sha256(password.encode()).hexdigest()
    return base64.b64encode(f"{username}:{digest}".encode()).decode()
