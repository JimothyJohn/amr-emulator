"""MiR-style Basic auth.

The real robot expects ``Authorization: Basic BASE64(<user>:SHA-256(<password>))``
where SHA-256(...) is the lower-case hex digest. The factory default account is
``distributor`` / ``distributor``, which the emulator mirrors.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac

DEFAULT_USERNAME = "distributor"
DEFAULT_PASSWORD = "distributor"  # noqa: S105 - MiR's documented factory default

MAX_HEADER_LENGTH = 8192


def expected_token(username: str, password: str) -> str:
    digest = hashlib.sha256(password.encode()).hexdigest()
    return base64.b64encode(f"{username}:{digest}".encode()).decode()


def is_authorized(header: str | None, username: str, password: str) -> bool:
    if not header or len(header) > MAX_HEADER_LENGTH:
        return False
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "basic" or not token:
        return False
    try:
        base64.b64decode(token.strip(), validate=True)
    except (binascii.Error, ValueError):
        return False
    return hmac.compare_digest(token.strip(), expected_token(username, password))
