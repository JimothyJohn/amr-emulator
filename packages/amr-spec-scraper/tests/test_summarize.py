"""AI summary step: strictly best-effort, key never leaks, output capped."""

import json

import httpx
import pytest
from amr_spec_scraper.summarize import (
    MAX_SUMMARY_CHARS,
    SummaryError,
    summarize_report,
    summarizer_from_env,
)

KEY = "sk-or-test-000"


def _transport(handler) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def _ok(content: str) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == f"Bearer {KEY}"
        body = json.loads(request.content)
        assert body["model"]
        assert body["messages"][1]["role"] == "user"
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    return _transport(handler)


def test_success_returns_summary():
    out = summarize_report("### API changes\n- added X", KEY, transport=_ok(" Impact: X. "))
    assert out == "Impact: X."


def test_oversized_summary_is_capped():
    out = summarize_report("diff", KEY, transport=_ok("y" * (MAX_SUMMARY_CHARS * 2)))
    assert len(out) == MAX_SUMMARY_CHARS


def test_oversized_report_is_truncated_before_sending():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["len"] = len(json.loads(request.content)["messages"][1]["content"])
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    summarize_report("d" * 100_000, KEY, transport=_transport(handler))
    assert seen["len"] == 24_000


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(500, text="boom"),
        httpx.Response(429, text="rate limited"),
        httpx.Response(200, json={"unexpected": True}),
        httpx.Response(200, json={"choices": [{"message": {"content": ""}}]}),
        httpx.Response(200, json={"choices": [{"message": {"content": None}}]}),
        httpx.Response(200, text="not json"),
    ],
)
def test_failures_raise_summary_error_without_leaking_key(response):
    def handler(_request: httpx.Request) -> httpx.Response:
        return response

    with pytest.raises(SummaryError) as exc_info:
        summarize_report("diff", KEY, transport=_transport(handler))
    assert KEY not in str(exc_info.value)
    assert "boom" not in str(exc_info.value)  # response bodies stay out of logs


def test_network_error_raises_summary_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route")

    with pytest.raises(SummaryError):
        summarize_report("diff", KEY, transport=_transport(handler))


def test_summarizer_from_env(monkeypatch):
    monkeypatch.delenv("OPEN_ROUTER_API_KEY", raising=False)
    assert summarizer_from_env() is None
    monkeypatch.setenv("OPEN_ROUTER_API_KEY", KEY)
    assert callable(summarizer_from_env())


def test_model_override_via_env(monkeypatch):
    monkeypatch.setenv("AMR_SUMMARY_MODEL", "anthropic/claude-haiku-4.5")
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["model"] = json.loads(request.content)["model"]
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    summarize_report("diff", KEY, transport=_transport(handler))
    assert seen["model"] == "anthropic/claude-haiku-4.5"
