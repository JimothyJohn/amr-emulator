"""Adversarial checks on the MiR-style Basic auth verifier."""

import base64

from amr_emulator.auth import expected_token, is_authorized
from hypothesis import given
from hypothesis import strategies as st


def _header(user: str, password: str) -> str:
    return f"Basic {expected_token(user, password)}"


def test_documented_distributor_token():
    # From the official spec's securityDefinitions example.
    assert expected_token("distributor", "distributor") == (
        "ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3"
        "NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=="
    )


def test_valid_header_passes():
    assert is_authorized(_header("distributor", "distributor"), "distributor", "distributor")


def test_wrong_password_fails():
    assert not is_authorized(_header("distributor", "nope"), "distributor", "distributor")


def test_plain_basic_auth_without_sha256_fails():
    raw = base64.b64encode(b"distributor:distributor").decode()
    assert not is_authorized(f"Basic {raw}", "distributor", "distributor")


def test_missing_empty_and_malformed_headers_fail():
    for header in [None, "", "Basic", "Basic ", "Bearer abc", "Basic not-base64!!"]:
        assert not is_authorized(header, "distributor", "distributor")


def test_oversized_header_fails_fast():
    assert not is_authorized("Basic " + "A" * 100_000, "distributor", "distributor")


@given(st.text(max_size=200))
def test_arbitrary_junk_never_authenticates(junk):
    if junk == _header("distributor", "distributor"):
        return
    assert not is_authorized(junk, "distributor", "distributor")


@given(st.binary(max_size=64))
def test_arbitrary_base64_payloads_never_authenticate(payload):
    token = base64.b64encode(payload).decode()
    if token == expected_token("distributor", "distributor"):
        return
    assert not is_authorized(f"Basic {token}", "distributor", "distributor")
