"""Serve every tracked MiR version from one AWS Lambda function.

Layout: each tracked version is mounted under its own prefix —
``/<mir_version>/api/v2.0.0/...`` (e.g. ``/3.8.1/api/v2.0.0/status``) —
plus a ``/latest`` alias for the newest tracked version and a JSON index
at ``/``. Version apps are built lazily on first hit so cold starts only
pay for the versions actually used.

The Lambda side is a hand-rolled API Gateway HTTP API (payload v2) → ASGI
adapter rather than a dependency: the emulator needs no streaming, no
websockets, and no lifespan events, so the full contract fits in ~80 lines
and stays inside the package's existing dependency set.
"""

from __future__ import annotations

import asyncio
import base64
import binascii
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from starlette.applications import Starlette
from starlette.datastructures import MutableHeaders
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route

from mir_emulator import registry
from mir_emulator.app import _SecurityHeadersMiddleware, create_app

# The emulator itself caps request bodies at 2 MiB; reject anything larger
# before it is even handed to the app (API Gateway allows up to 10 MB).
MAX_EVENT_BODY_BYTES = 4 * 1024 * 1024

# Site pages, bundled next to this module by scripts/deploy_demo.sh. Absent
# in normal installs, where the HTML routes 404 and / stays JSON. The landing
# page (docs/landing.html) is served at / to clients that prefer HTML; the
# MiR console keeps /console (plus /mir), and the VDA 5050, Omron ARCL, and
# MassRobotics app pages get their own routes. curl and API clients keep the
# JSON index.
CONSOLE_FILE = Path(__file__).with_name("console.html")
LANDING_FILE = Path(__file__).with_name("landing.html")
SITE_PAGES = {
    "vda5050": Path(__file__).with_name("vda5050.html"),
    "omron": Path(__file__).with_name("omron.html"),
    "massrobotics": Path(__file__).with_name("massrobotics.html"),
}

# The console is a single inline-script page (hence 'unsafe-inline'); it
# fetches Google Fonts and, via its ?api= override, talks to arbitrary
# user-chosen emulator endpoints — hence the broad connect-src (also covers
# localhost robots over plain HTTP).
CONSOLE_CSP = (
    "default-src 'none'; "
    "style-src 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "script-src 'unsafe-inline'; "
    "img-src data:; "
    "connect-src https: http://127.0.0.1:* http://localhost:*; "
    "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)


class _HstsMiddleware:
    """The public deployment is HTTPS-only (API Gateway terminates TLS);
    pin browsers to it."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_hsts(message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.setdefault(
                    "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
                )
            await send(message)

        await self.app(scope, receive, send_with_hsts)


class _LazyVersionApp:
    """Builds the per-version emulator app on first request, then delegates."""

    def __init__(self, version: str, factory=create_app) -> None:
        self.version = version
        self._factory = factory
        self._app: Starlette | None = None
        self._lock = asyncio.Lock()

    async def __call__(self, scope, receive, send) -> None:
        if self._app is None:
            async with self._lock:
                if self._app is None:
                    self._app = self._factory(self.version)
        await self._app(scope, receive, send)


def build_app() -> Starlette:
    """Top-level dispatcher: /<version>/... , /fleet/<version>/... , / index."""
    from mir_emulator.fleet import create_fleet_app

    versions = registry.supported_versions()
    version_apps = {v: _LazyVersionApp(v) for v in versions}
    latest = versions[0]
    fleet_versions = registry.fleet_supported_versions()
    fleet_apps = {v: _LazyVersionApp(v, factory=create_fleet_app) for v in fleet_versions}

    async def index(request: Request) -> HTMLResponse | JSONResponse:
        page = LANDING_FILE if LANDING_FILE.is_file() else CONSOLE_FILE
        if "text/html" in request.headers.get("accept", "") and page.is_file():
            return HTMLResponse(
                page.read_text("utf-8"),
                headers={
                    "Content-Security-Policy": CONSOLE_CSP,
                    "Vary": "Accept",
                },
            )
        base = str(request.base_url).rstrip("/")
        return JSONResponse(
            {
                "name": "mir-emulator",
                "description": (
                    "Emulator of the MiR robot REST API. Each tracked MiR software "
                    "version is served under its own path prefix."
                ),
                "primary_source": registry.primary_source(),
                "versions": {v: f"{base}/{v}/api/v2.0.0" for v in versions},
                "latest": f"{base}/latest/api/v2.0.0",
                "fleet": {
                    "description": (
                        "MiR Fleet Enterprise Integration API emulator; each fleet "
                        "embeds robot emulators it controls over their own REST API"
                    ),
                    "versions": {v: f"{base}/fleet/{v}/api/v1" for v in fleet_versions},
                    "auth": "x-api-key header; default key 'distributor'",
                    "specs": {v: f"{base}/fleet/{v}/openapi.json" for v in fleet_versions},
                    "official_docs": {
                        v: registry.fleet_registry()
                        .get("docs_url_template", "")
                        .replace("{version}", v)
                        for v in fleet_versions
                    },
                },
                "auth": (
                    "Authorization: Basic BASE64(user:SHA-256-hex(password)); "
                    "factory default account distributor/distributor"
                ),
                "specs": {v: f"{base}/{v}/swagger.json" for v in versions},
                "console": f"{base}/console",
                "diff": f"{base}/_emulator/diff?from=2.14.7&to=3.8.1",
                "sessions": (
                    "Send X-MiR-Session: <1-64 chars of A-Za-z0-9._-> to control your own "
                    "isolated virtual robot; omit it for the shared default robot"
                ),
                "notes": (
                    "Shared demo instance: state is in-memory, per runtime instance, "
                    "and reset on cold start. Do not store anything you need to keep."
                ),
            }
        )

    async def emulator_diff(request: Request) -> JSONResponse:
        from mir_emulator.diff import diff_versions

        from_version = request.query_params.get("from", "")
        to_version = request.query_params.get("to", "")
        if not from_version or not to_version:
            return JSONResponse(
                {
                    "error_code": "400",
                    "error_human": "provide ?from=<version>&to=<version> (tracked versions; "
                    "robot or fleet, not mixed)",
                },
                status_code=400,
            )
        try:
            return JSONResponse(diff_versions(from_version, to_version))
        except KeyError as exc:
            return JSONResponse(
                {"error_code": "404", "error_human": str(exc.args[0])}, status_code=404
            )
        except ValueError as exc:
            return JSONResponse({"error_code": "400", "error_human": str(exc)}, status_code=400)

    async def healthz(_request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "ok",
                "kind": "dispatcher",
                "versions": versions,
                "latest": latest,
                "fleet_versions": fleet_versions,
                "fleet_latest": fleet_versions[0] if fleet_versions else None,
            }
        )

    async def console(_request: Request) -> HTMLResponse | JSONResponse:
        if not CONSOLE_FILE.is_file():
            return JSONResponse(
                {"error_code": "404", "error_human": "Console page not bundled in this build"},
                status_code=404,
            )
        return HTMLResponse(
            CONSOLE_FILE.read_text("utf-8"),
            headers={"Content-Security-Policy": CONSOLE_CSP},
        )

    def _page_route(page_path: Path):
        async def page(_request: Request) -> HTMLResponse | JSONResponse:
            if not page_path.is_file():
                return JSONResponse(
                    {"error_code": "404", "error_human": "Page not bundled in this build"},
                    status_code=404,
                )
            return HTMLResponse(
                page_path.read_text("utf-8"),
                headers={"Content-Security-Policy": CONSOLE_CSP},
            )

        return page

    async def not_found(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(
            {
                "error_code": "404",
                "error_human": "Not found. See / for the list of MiR versions and paths.",
            },
            status_code=404,
        )

    async def method_not_allowed(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(
            {
                "error_code": "405",
                "error_human": "Method not allowed on this path.",
            },
            status_code=405,
        )

    routes: list[Route | Mount] = [
        Route("/", index),
        Route("/healthz", healthz),
        Route("/_emulator/diff", emulator_diff),
        Route("/console", console),
        Route("/mir", console),
        *[Route(f"/{name}", _page_route(path)) for name, path in SITE_PAGES.items()],
        Mount("/latest", app=version_apps[latest]),
        *[Mount(f"/fleet/{v}", app=app) for v, app in fleet_apps.items()],
        *([Mount("/fleet/latest", app=fleet_apps[fleet_versions[0]])] if fleet_versions else []),
        *[Mount(f"/{v}", app=app) for v, app in version_apps.items()],
    ]
    middleware = [
        Middleware(_SecurityHeadersMiddleware),
        Middleware(_HstsMiddleware),
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=86400,
        ),
    ]
    return Starlette(
        routes=routes,
        exception_handlers={404: not_found, 405: method_not_allowed},
        middleware=middleware,
    )


def _event_headers(event: dict) -> list[tuple[bytes, bytes]]:
    headers = [
        (str(k).lower().encode("utf-8"), str(v).encode("utf-8"))
        for k, v in (event.get("headers") or {}).items()
    ]
    cookies = event.get("cookies") or []
    if cookies:
        headers.append((b"cookie", "; ".join(cookies).encode("utf-8")))
    return headers


def _asgi_scope(event: dict) -> dict:
    http = event.get("requestContext", {}).get("http", {})
    raw_path = event.get("rawPath") or "/"
    host = (event.get("headers") or {}).get("host", "lambda")
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": str(http.get("protocol", "HTTP/1.1")).rpartition("/")[2],
        "method": str(http.get("method", "GET")).upper(),
        "scheme": "https",
        "path": unquote(raw_path),
        "raw_path": raw_path.encode("utf-8"),
        "query_string": (event.get("rawQueryString") or "").encode("utf-8"),
        "root_path": "",
        "headers": _event_headers(event),
        "client": (http.get("sourceIp", ""), 0),
        "server": (host, 443),
    }


def _event_body(event: dict) -> bytes | None:
    """Request body bytes, or None if the event is malformed/oversized."""
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        try:
            raw = base64.b64decode(body, validate=True)
        except (binascii.Error, ValueError):
            return None
    else:
        raw = body.encode("utf-8")
    if len(raw) > MAX_EVENT_BODY_BYTES:
        return None
    return raw


def _http_response(status: int, headers: list, body: bytes) -> dict:
    out_headers: dict[str, str] = {}
    cookies: list[str] = []
    for key_b, value_b in headers:
        key = key_b.decode("latin-1")
        value = value_b.decode("latin-1")
        if key.lower() == "set-cookie":
            cookies.append(value)
        elif key.lower() in out_headers:
            out_headers[key.lower()] += f", {value}"
        else:
            out_headers[key.lower()] = value
    response: dict[str, Any] = {"statusCode": status, "headers": out_headers, "cookies": cookies}
    try:
        response["body"] = body.decode("utf-8")
        response["isBase64Encoded"] = False
    except UnicodeDecodeError:
        response["body"] = base64.b64encode(body).decode("ascii")
        response["isBase64Encoded"] = True
    return response


async def _invoke(app, event: dict) -> dict:
    body = _event_body(event)
    if body is None:
        return _http_response(
            400,
            [(b"content-type", b"application/json")],
            b'{"error_code": "400", "error_human": "Malformed or oversized request body"}',
        )

    consumed = False

    async def receive() -> dict:
        nonlocal consumed
        if not consumed:
            consumed = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    status = 500
    response_headers: list = []
    chunks: list[bytes] = []

    async def send(message: dict) -> None:
        nonlocal status, response_headers
        if message["type"] == "http.response.start":
            status = message["status"]
            response_headers = list(message.get("headers") or [])
        elif message["type"] == "http.response.body":
            chunks.append(bytes(message.get("body") or b""))

    await app(_asgi_scope(event), receive, send)
    return _http_response(status, response_headers, b"".join(chunks))


_app: Starlette | None = None


def handler(event: dict, _context: Any = None) -> dict:
    """AWS Lambda entry point (API Gateway HTTP API, payload format 2.0)."""
    global _app  # warm-container cache is the point
    if _app is None:
        _app = build_app()
    return asyncio.run(_invoke(_app, event))
