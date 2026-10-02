"""MiR support portal client.

The portal (Umbraco) has a server-side login wall; a free account is enough.
Credentials come from MIR_PORTAL_EMAIL / MIR_PORTAL_PASSWORD. The login form
observed on the live portal posts email/password/returnUrl to
/umbraco/surface/user/LoginWebsite.

The file-listing parser is deliberately forgiving: it collects every anchor
whose href or text looks like an API definition file with a version in it,
because the authenticated page's exact markup can change between portal
releases.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

from amr_spec_scraper.versions import format_version, parse_version

PORTAL_BASE = "https://supportportal.mobile-industrial-robots.com"
FILES_PAGE = "/documentation/rest-api/rest-api-files/"
LOGIN_ENDPOINT = "/umbraco/surface/user/LoginWebsite"

FILE_HINT_RE = re.compile(r"(rest[-_ ]?api|swagger|openapi)", re.IGNORECASE)
SPEC_EXTENSIONS = (".json", ".yaml", ".yml", ".zip")

# Largest observed portal PDF is ~9 MB; 64 MB leaves headroom while bounding
# memory if the portal (or a tampered listing) ever serves something huge.
MAX_DOWNLOAD_BYTES = 64 * 1024 * 1024


@dataclass(frozen=True)
class PortalFile:
    version: tuple[int, ...]
    url: str
    label: str

    @property
    def version_str(self) -> str:
        return format_version(self.version)


class _AnchorCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[tuple[str, str]] = []  # (href, text)
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._flush()
            self._href = dict(attrs).get("href") or ""
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def _flush(self) -> None:
        if self._href is not None:
            self.anchors.append((self._href, " ".join(self._text).strip()))
        self._href = None
        self._text = []

    def close(self) -> None:
        self._flush()
        super().close()


def parse_file_listing(html: str, base_url: str = PORTAL_BASE + FILES_PAGE) -> list[PortalFile]:
    parser = _AnchorCollector()
    parser.feed(html)
    parser.close()

    found: dict[tuple[tuple[int, ...], str], PortalFile] = {}
    for href, text in parser.anchors:
        blob = f"{href} {text}"
        version = parse_version(blob)
        if version is None:
            continue
        looks_like_spec = href.lower().endswith(SPEC_EXTENSIONS) or FILE_HINT_RE.search(blob)
        if not looks_like_spec:
            continue
        url = urljoin(base_url, href)
        found[(version, url)] = PortalFile(version=version, url=url, label=text or href)
    return sorted(found.values(), key=lambda f: (f.version, f.url), reverse=True)


class PortalClient:
    def __init__(
        self,
        email: str,
        password: str,
        base_url: str = PORTAL_BASE,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """`transport` is a test seam (httpx.MockTransport) so the sync state
        machine can be exercised offline; live behavior is covered by the
        live_portal-marked tests."""
        self.base_url = base_url
        self._email = email
        self._password = password
        self._http = httpx.Client(
            base_url=base_url,
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "amr-emulator-spec-scraper/1.0"},
            transport=transport,
        )

    def login(self) -> None:
        response = self._http.post(
            LOGIN_ENDPOINT,
            data={
                "email": self._email,
                "password": self._password,
                "returnUrl": FILES_PAGE,
            },
        )
        response.raise_for_status()
        if "LoginWebsite" in str(response.url) or 'name="password"' in response.text:
            raise PermissionError(
                "portal login was rejected; check MIR_PORTAL_EMAIL/MIR_PORTAL_PASSWORD"
            )

    def list_files(self) -> list[PortalFile]:
        response = self._http.get(FILES_PAGE)
        response.raise_for_status()
        if 'name="password"' in response.text:
            raise PermissionError("not logged in: portal returned the login page")
        return parse_file_listing(response.text, str(response.url))

    def download(self, file: PortalFile) -> bytes:
        """Fetch a listed file — only over HTTPS from the portal's own host,
        and never more than MAX_DOWNLOAD_BYTES (the listing is scraped HTML;
        treat every URL in it as attacker-influenced until proven otherwise)."""
        url = httpx.URL(file.url)
        allowed_host = httpx.URL(self.base_url).host
        if url.scheme != "https" or url.host != allowed_host:
            raise ValueError(f"refusing to download from {file.url!r}: not https://{allowed_host}")
        with self._http.stream("GET", file.url) as response:
            response.raise_for_status()
            declared = int(response.headers.get("content-length") or 0)
            if declared > MAX_DOWNLOAD_BYTES:
                raise ValueError(f"{file.url} declares {declared} bytes (cap {MAX_DOWNLOAD_BYTES})")
            chunks: list[bytes] = []
            received = 0
            for chunk in response.iter_bytes():
                received += len(chunk)
                if received > MAX_DOWNLOAD_BYTES:
                    raise ValueError(f"{file.url} exceeded {MAX_DOWNLOAD_BYTES} byte cap")
                chunks.append(chunk)
        return b"".join(chunks)

    def close(self) -> None:
        self._http.close()
