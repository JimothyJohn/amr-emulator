"""Contract + adversarial tests for the Lambda multi-version dispatcher.

Everything goes through the real API Gateway HTTP API v2 event shape and
the real bundled specs — the handler is exactly what runs in Lambda.
"""

import base64
import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from mir_emulator import registry, serverless
from mir_emulator.auth import expected_token

AUTH = f"Basic {expected_token('distributor', 'distributor')}"


def event(
    method: str = "GET",
    path: str = "/",
    *,
    headers: dict | None = None,
    body: str | None = None,
    is_base64: bool = False,
    query: str = "",
    cookies: list | None = None,
) -> dict:
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": query,
        "cookies": cookies or [],
        "headers": {"host": "demo.example.com", **(headers or {})},
        "requestContext": {
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "203.0.113.7",
            }
        },
        "body": body,
        "isBase64Encoded": is_base64,
    }


@pytest.fixture(scope="module", autouse=True)
def _pristine_site_pages(tmp_path_factory):
    """Local previews stage real site pages next to the module (gitignored);
    these tests assert both bundled and unbundled behavior, so pin the page
    paths to a private empty directory regardless of workstation state.
    Function-scoped monkeypatches in individual tests still override this."""
    mp = pytest.MonkeyPatch()
    empty = tmp_path_factory.mktemp("no-pages")
    mp.setattr(serverless, "CONSOLE_FILE", empty / "console.html")
    mp.setattr(serverless, "LANDING_FILE", empty / "landing.html")
    mp.setattr(serverless, "SITE_PAGES", {k: empty / f"{k}.html" for k in serverless.SITE_PAGES})
    yield
    mp.undo()


@pytest.fixture(scope="module")
def call():
    """One warm 'container' for the module: same cached app across calls."""
    serverless._app = None
    yield lambda ev: serverless.handler(ev, None)
    serverless._app = None


def body_json(response: dict) -> dict:
    assert not response["isBase64Encoded"]
    return json.loads(response["body"])


def test_index_lists_every_tracked_version(call):
    response = call(event("GET", "/"))
    assert response["statusCode"] == 200
    doc = body_json(response)
    for version in registry.supported_versions():
        assert doc["versions"][version].endswith(f"/{version}/api/v2.0.0")
    assert "/latest/api/v2.0.0" in doc["latest"]
    assert doc["console"].endswith("/console")


def test_healthz(call):
    response = call(event("GET", "/healthz"))
    assert response["statusCode"] == 200
    doc = body_json(response)
    assert doc["status"] == "ok"
    assert doc["kind"] == "dispatcher"
    assert doc["versions"] == registry.supported_versions()
    assert doc["latest"] == registry.supported_versions()[0]
    assert doc["fleet_versions"] == registry.fleet_supported_versions()
    assert doc["fleet_latest"] == registry.fleet_supported_versions()[0]


def test_index_lists_fleet_versions(call):
    doc = body_json(call(event("GET", "/")))
    for version in registry.fleet_supported_versions():
        assert doc["fleet"]["versions"][version].endswith(f"/fleet/{version}/api/v1")
        assert doc["fleet"]["official_docs"][version].startswith("https://supportportal")


def test_fleet_mount_serves_the_fleet_api(call):
    denied = call(event("GET", "/fleet/1.5.0/api/v1/robots"))
    assert denied["statusCode"] == 401
    allowed = call(event("GET", "/fleet/1.5.0/api/v1/robots", headers={"x-api-key": "distributor"}))
    assert allowed["statusCode"] == 200
    assert len(body_json(allowed)["robots"]) == 2
    latest = call(event("GET", "/fleet/latest/"))
    assert body_json(latest)["emulated_fleet_version"] == registry.fleet_supported_versions()[0]


def test_console_404s_when_not_bundled(call):
    # Normal installs don't ship console.html; only the Lambda bundle does.
    if serverless.CONSOLE_FILE.is_file():
        pytest.skip("console.html present in this environment")
    response = call(event("GET", "/console"))
    assert response["statusCode"] == 404


def test_index_stays_json_for_api_clients_even_when_console_bundled(call, tmp_path, monkeypatch):
    # curl sends Accept: */* — the JSON contract must survive the HTML page.
    page = tmp_path / "console.html"
    page.write_text("<!DOCTYPE html><title>console</title>", encoding="utf-8")
    monkeypatch.setattr(serverless, "CONSOLE_FILE", page)
    for accept in ({}, {"accept": "*/*"}, {"accept": "application/json"}):
        response = call(event("GET", "/", headers=accept))
        assert response["statusCode"] == 200
        assert "application/json" in response["headers"]["content-type"]
        assert "versions" in body_json(response)


def test_index_serves_console_page_to_browsers(call, tmp_path, monkeypatch):
    # Landing page and console are the same document — parity by construction.
    page = tmp_path / "console.html"
    page.write_text("<!DOCTYPE html><title>console</title>", encoding="utf-8")
    monkeypatch.setattr(serverless, "CONSOLE_FILE", page)
    browser_accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    landing = call(event("GET", "/", headers={"accept": browser_accept}))
    assert landing["statusCode"] == 200
    assert "text/html" in landing["headers"]["content-type"]
    assert "console" in landing["body"]
    assert landing["headers"]["vary"] == "Accept"
    csp = landing["headers"]["content-security-policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp
    assert landing["headers"]["x-content-type-options"] == "nosniff"
    console = call(event("GET", "/console"))
    assert console["body"] == landing["body"]
    assert console["headers"]["content-security-policy"] == csp


def test_index_serves_json_to_browsers_when_console_not_bundled(call, monkeypatch):
    monkeypatch.setattr(serverless, "CONSOLE_FILE", serverless.CONSOLE_FILE.parent / "absent.html")
    response = call(event("GET", "/", headers={"accept": "text/html"}))
    assert response["statusCode"] == 200
    assert "application/json" in response["headers"]["content-type"]


def test_index_json_names_the_primary_source(call):
    doc = body_json(call(event("GET", "/")))
    assert doc["primary_source"].startswith("https://")
    for version in registry.supported_versions():
        version_index = body_json(call(event("GET", f"/{version}/")))
        source = version_index["source"]
        assert source["primary_source"] == doc["primary_source"]
        assert source["provenance"]
        assert source["official"] is True


def test_console_serves_bundled_page_with_csp(call, tmp_path, monkeypatch):
    page = tmp_path / "console.html"
    page.write_text("<!DOCTYPE html><title>fleet console</title>", encoding="utf-8")
    monkeypatch.setattr(serverless, "CONSOLE_FILE", page)
    response = call(event("GET", "/console"))
    assert response["statusCode"] == 200
    assert "text/html" in response["headers"]["content-type"]
    assert "fleet console" in response["body"]
    csp = response["headers"]["content-security-policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp
    # security headers still apply to the console
    assert response["headers"]["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize("name", sorted(serverless.SITE_PAGES))
def test_site_pages_serve_bundled_page_with_csp(call, tmp_path, monkeypatch, name):
    # _page_route captures page paths when the app is built, so stage the
    # page first and force this invocation to rebuild.
    page = tmp_path / f"{name}.html"
    page.write_text(f"<!DOCTYPE html><title>{name} app page</title>", encoding="utf-8")
    monkeypatch.setitem(serverless.SITE_PAGES, name, page)
    monkeypatch.setattr(serverless, "_app", None)
    response = call(event("GET", f"/{name}"))
    assert response["statusCode"] == 200
    assert "text/html" in response["headers"]["content-type"]
    assert f"{name} app page" in response["body"]
    csp = response["headers"]["content-security-policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_site_pages_404_when_not_bundled(call):
    for name in serverless.SITE_PAGES:
        response = call(event("GET", f"/{name}"))
        assert response["statusCode"] == 404
        assert body_json(response)["error_code"] == "404"


def test_console_csp_script_src_is_pinned():
    # The console is a single inline-script page with no third-party scripts;
    # script-src must stay exactly 'unsafe-inline' and nothing broader.
    # Widening this list (e.g. to re-add a CDN) is a supply-chain decision —
    # do it in a deliberate diff and update this test in the same commit.
    # (That the served /console header carries CONSOLE_CSP is covered by the
    # bundled-page tests above; this test pins the allowlist itself.)
    csp = serverless.CONSOLE_CSP
    directives = {p[0]: p[1:] for p in (d.split(" ") for d in csp.split("; "))}
    assert directives["default-src"] == ["'none'"]
    assert set(directives["script-src"]) == {"'unsafe-inline'"}
    # no eval of any kind, and connections stay HTTPS-or-loopback only
    assert "'unsafe-eval'" not in csp
    assert "wasm-unsafe-eval" not in csp
    assert all(
        source.startswith(("https:", "http://127.0.0.1", "http://localhost"))
        for source in directives["connect-src"]
    )


def test_every_version_serves_status_with_auth(call):
    for version in registry.supported_versions():
        response = call(
            event("GET", f"/{version}/api/v2.0.0/status", headers={"authorization": AUTH})
        )
        assert response["statusCode"] == 200, version
        doc = body_json(response)
        assert "robot_name" in doc or "state_text" in doc


def test_latest_alias_matches_newest_version(call):
    newest = registry.supported_versions()[0]
    via_alias = call(event("GET", "/latest/swagger.json"))
    via_version = call(event("GET", f"/{newest}/swagger.json"))
    assert via_alias["statusCode"] == via_version["statusCode"] == 200
    assert body_json(via_alias)["info"] == body_json(via_version)["info"]


def test_missing_auth_is_401(call):
    response = call(event("GET", "/3.8.1/api/v2.0.0/status"))
    assert response["statusCode"] == 401
    assert body_json(response)["error_code"] == "401"


def test_wrong_password_is_401(call):
    bad = f"Basic {expected_token('distributor', 'wrong')}"
    response = call(event("GET", "/3.8.1/api/v2.0.0/status", headers={"authorization": bad}))
    assert response["statusCode"] == 401


def test_unknown_version_prefix_is_404_json(call):
    response = call(event("GET", "/9.9.9/api/v2.0.0/status", headers={"authorization": AUTH}))
    assert response["statusCode"] == 404
    assert body_json(response)["error_code"] == "404"


def seeded_mission_guid(call, version: str) -> str:
    """A mission the emulated robot actually knows — enqueueing anything else
    is rejected with 400, exactly like a real robot."""
    listing = call(event("GET", f"/{version}/api/v2.0.0/missions", headers={"authorization": AUTH}))
    assert listing["statusCode"] == 200
    return json.loads(listing["body"])[0]["guid"]


def test_state_survives_across_invocations_within_container(call):
    mission = seeded_mission_guid(call, "3.8.1")
    enqueue = call(
        event(
            "POST",
            "/3.8.1/api/v2.0.0/mission_queue",
            headers={"authorization": AUTH, "content-type": "application/json"},
            body=json.dumps({"mission_id": mission}),
        )
    )
    assert enqueue["statusCode"] == 201
    listing = call(event("GET", "/3.8.1/api/v2.0.0/mission_queue", headers={"authorization": AUTH}))
    assert listing["statusCode"] == 200
    assert any(entry.get("state") == "Pending" for entry in json.loads(listing["body"])), (
        "enqueued mission should be visible on a later invocation of the same container"
    )


def test_versions_do_not_share_state(call):
    enqueue = call(
        event(
            "POST",
            "/3.7.2/api/v2.0.0/mission_queue",
            headers={"authorization": AUTH},
            body=json.dumps({"mission_id": seeded_mission_guid(call, "3.7.2")}),
        )
    )
    assert enqueue["statusCode"] == 201
    old = call(event("GET", "/2.14.7/api/v2.0.0/mission_queue", headers={"authorization": AUTH}))
    assert old["statusCode"] == 200
    assert json.loads(old["body"]) == [], "3.7.2's queue entry must not appear on 2.14.7"


def test_unknown_mission_id_is_rejected_like_a_real_robot(call):
    response = call(
        event(
            "POST",
            "/3.8.1/api/v2.0.0/mission_queue",
            headers={"authorization": AUTH},
            body=json.dumps({"mission_id": "no-such-mission-guid"}),
        )
    )
    assert response["statusCode"] == 400
    assert "Argument error" in body_json(response)["error_human"]


def test_base64_encoded_body_is_decoded(call):
    mission = seeded_mission_guid(call, "3.8.1")
    payload = base64.b64encode(json.dumps({"mission_id": mission}).encode()).decode()
    response = call(
        event(
            "POST",
            "/3.8.1/api/v2.0.0/mission_queue",
            headers={"authorization": AUTH},
            body=payload,
            is_base64=True,
        )
    )
    assert response["statusCode"] == 201
    # The 201 alone proves the body decoded (an unknown mission_id is a 400);
    # the queued entry names the mission at the item endpoint.
    queue_id = body_json(response)["id"]
    item = call(
        event(
            "GET",
            f"/3.8.1/api/v2.0.0/mission_queue/{queue_id}",
            headers={"authorization": AUTH},
        )
    )
    assert body_json(item)["mission_id"] == mission


def test_malformed_base64_body_is_400_not_crash(call):
    response = call(
        event(
            "POST",
            "/3.8.1/api/v2.0.0/mission_queue",
            headers={"authorization": AUTH},
            body="!!!not-base64!!!",
            is_base64=True,
        )
    )
    assert response["statusCode"] == 400


def test_oversized_body_is_rejected(call):
    response = call(
        event(
            "POST",
            "/3.8.1/api/v2.0.0/mission_queue",
            headers={"authorization": AUTH},
            body="x" * (serverless.MAX_EVENT_BODY_BYTES + 1),
        )
    )
    assert response["statusCode"] == 400


def test_invalid_json_body_is_400(call):
    response = call(
        event(
            "POST",
            "/3.8.1/api/v2.0.0/mission_queue",
            headers={"authorization": AUTH},
            body="{not json",
        )
    )
    assert response["statusCode"] == 400
    assert body_json(response)["error_code"] == "400"


def test_cors_preflight(call):
    response = call(
        event(
            "OPTIONS",
            "/3.8.1/api/v2.0.0/status",
            headers={
                "origin": "https://example.github.io",
                "access-control-request-method": "GET",
                "access-control-request-headers": "authorization",
            },
        )
    )
    assert response["statusCode"] == 200
    assert response["headers"]["access-control-allow-origin"] == "*"
    assert "GET" in response["headers"]["access-control-allow-methods"]


def test_cors_header_on_actual_response(call):
    response = call(
        event(
            "GET",
            "/3.8.1/api/v2.0.0/status",
            headers={"authorization": AUTH, "origin": "https://example.github.io"},
        )
    )
    assert response["headers"]["access-control-allow-origin"] == "*"


def test_security_headers_present(call):
    for path in ["/", "/3.8.1/api/v2.0.0/status", "/nope"]:
        response = call(event("GET", path))
        assert response["headers"]["x-content-type-options"] == "nosniff"
        assert "strict-transport-security" in response["headers"]


def test_percent_encoded_traversal_is_404(call):
    response = call(
        event("GET", "/3.8.1/%2e%2e/%2e%2e/etc/passwd", headers={"authorization": AUTH})
    )
    assert response["statusCode"] == 404
    assert body_json(response)["error_code"] == "404"


def test_query_string_reaches_the_app(call):
    response = call(
        event(
            "GET",
            "/3.8.1/api/v2.0.0/missions",
            headers={"authorization": AUTH},
            query="whitelist=name&limit=5",
        )
    )
    assert response["statusCode"] == 200


def test_metrics_returns_text_not_base64(call):
    response = call(event("GET", "/3.8.1/api/v2.0.0/metrics", headers={"authorization": AUTH}))
    if response["statusCode"] == 200:  # only some versions expose /metrics
        assert not response["isBase64Encoded"]
        assert "text" in response["headers"].get("content-type", "")


def test_unicode_header_values_do_not_crash(call):
    response = call(
        event(
            "GET",
            "/",
            headers={
                "user-agent": "\u043c\u0456\u0440-client \u00ff \u2028",
                "x-junk": "\U0001f916",
            },
        )
    )
    assert response["statusCode"] == 200


def test_cookies_are_forwarded_not_crashing(call):
    response = call(event("GET", "/", cookies=["session=abc123", "theme=dark"]))
    assert response["statusCode"] == 200


def test_duplicate_response_headers_are_comma_joined():
    response = serverless._http_response(200, [(b"x-multi", b"a"), (b"X-Multi", b"b")], b"{}")
    assert response["headers"]["x-multi"] == "a, b"


def test_binary_body_round_trips_as_base64():
    response = serverless._http_response(200, [], b"\x89PNG\r\n\x1a\n\x00\xff")
    assert response["isBase64Encoded"]
    assert base64.b64decode(response["body"]) == b"\x89PNG\r\n\x1a\n\x00\xff"


@settings(max_examples=40, deadline=None)
@given(
    method=st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "TRACE"]),
    path=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), min_size=0, max_size=80).map(
        lambda s: "/" + s
    ),
    query=st.text(max_size=60),
    body=st.one_of(st.none(), st.text(max_size=200)),
)
def test_arbitrary_requests_never_crash_the_handler(method, path, query, body):
    response = serverless.handler(
        event(method, path, headers={"authorization": AUTH}, body=body, query=query), None
    )
    assert isinstance(response["statusCode"], int)
    assert 200 <= response["statusCode"] < 600


def test_diff_endpoint_serves_upgrade_preflight(call):
    ok = call(event("GET", "/_emulator/diff", query="from=2.14.7&to=3.8.1"))
    assert ok["statusCode"] == 200
    doc = body_json(ok)
    assert doc["from"] == "2.14.7" and doc["to"] == "3.8.1"
    assert not doc["structurally_identical"]

    oracle = body_json(call(event("GET", "/_emulator/diff", query="from=3.5.4&to=3.5.6")))
    assert oracle["structurally_identical"]

    missing = call(event("GET", "/_emulator/diff"))
    assert missing["statusCode"] == 400
    unknown = call(event("GET", "/_emulator/diff", query="from=9.9.9&to=3.8.1"))
    assert unknown["statusCode"] == 404
    mixed = call(event("GET", "/_emulator/diff", query="from=3.8.1&to=1.5.0"))
    assert mixed["statusCode"] == 400
    assert "family" in body_json(mixed)["error_human"]
