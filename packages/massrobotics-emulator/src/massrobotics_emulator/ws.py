"""Minimal RFC 6455 WebSocket transport, stdlib asyncio only.

Implements exactly what the MassRobotics AMR Interop Standard needs — text
messages between a robot (client) and a receiver (server) — the same way the
VDA 5050 package hand-rolls its MQTT stack: no runtime dependencies, and the
protocol edges (masking rules, fragmentation, control-frame limits, close
codes) enforced strictly enough that a misbehaving peer is rejected instead
of silently tolerated.

Not implemented (and not needed here): extensions/compression, subprotocol
negotiation, and TLS (wrap the streams externally if ever required).
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import hashlib
import os
import secrets
from urllib.parse import urlsplit

_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

OP_CONT = 0x0
OP_TEXT = 0x1
OP_BINARY = 0x2
OP_CLOSE = 0x8
OP_PING = 0x9
OP_PONG = 0xA

MAX_MESSAGE_BYTES = 4 * 1024 * 1024
MAX_HEADER_BYTES = 16 * 1024


class WSError(Exception):
    """Protocol violation; ``code`` is the close code that applies."""

    def __init__(self, message: str, code: int = 1002) -> None:
        super().__init__(message)
        self.code = code


class WSClosed(Exception):
    """The peer closed the connection (or it dropped)."""

    def __init__(self, code: int | None = None, reason: str = "") -> None:
        super().__init__(f"websocket closed (code={code}, reason={reason!r})")
        self.code = code
        self.reason = reason


def _accept_value(key: str) -> str:
    digest = hashlib.sha1((key + _GUID).encode()).digest()  # noqa: S324 - mandated by RFC 6455
    return base64.b64encode(digest).decode()


class WebSocket:
    """One established connection; symmetric except for the masking role."""

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        *,
        mask_outgoing: bool,
        max_message_bytes: int = MAX_MESSAGE_BYTES,
    ) -> None:
        self._reader = reader
        self._writer = writer
        self._mask_outgoing = mask_outgoing
        self._max_message_bytes = max_message_bytes
        self._send_lock = asyncio.Lock()
        self.closed = False
        self.close_code: int | None = None

    # -- sending ---------------------------------------------------------

    async def send_text(self, text: str) -> None:
        await self._send_frame(OP_TEXT, text.encode())

    async def ping(self, payload: bytes = b"") -> None:
        await self._send_frame(OP_PING, payload)

    async def close(self, code: int = 1000, reason: str = "") -> None:
        if self.closed:
            return
        self.closed = True
        self.close_code = code
        payload = code.to_bytes(2, "big") + reason.encode()[:123]
        with contextlib.suppress(ConnectionError, RuntimeError):
            await self._send_frame(OP_CLOSE, payload, even_if_closed=True)
        try:
            self._writer.close()
            await self._writer.wait_closed()
        except (ConnectionError, OSError):
            pass

    async def _send_frame(
        self, opcode: int, payload: bytes, *, even_if_closed: bool = False
    ) -> None:
        if self.closed and not even_if_closed:
            raise WSClosed(self.close_code)
        head = bytearray([0x80 | opcode])
        mask_bit = 0x80 if self._mask_outgoing else 0
        length = len(payload)
        if length < 126:
            head.append(mask_bit | length)
        elif length < 1 << 16:
            head.append(mask_bit | 126)
            head += length.to_bytes(2, "big")
        else:
            head.append(mask_bit | 127)
            head += length.to_bytes(8, "big")
        if self._mask_outgoing:
            mask = secrets.token_bytes(4)
            head += mask
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        async with self._send_lock:
            self._writer.write(bytes(head) + payload)
            await self._writer.drain()

    # -- receiving -------------------------------------------------------

    async def receive_text(self) -> str:
        """Next complete text message; pings are answered transparently."""
        message = bytearray()
        expecting_continuation = False
        while True:
            fin, opcode, payload = await self._read_frame()
            if opcode == OP_PING:
                await self._send_frame(OP_PONG, payload)
                continue
            if opcode == OP_PONG:
                continue
            if opcode == OP_CLOSE:
                code = int.from_bytes(payload[:2], "big") if len(payload) >= 2 else None
                reason = payload[2:].decode("utf-8", "replace")
                await self.close(code or 1000)
                raise WSClosed(code, reason)
            if opcode == OP_CONT:
                if not expecting_continuation:
                    raise await self._fail("continuation frame with nothing to continue")
            elif opcode in (OP_TEXT, OP_BINARY):
                if expecting_continuation:
                    raise await self._fail("interleaved data frame inside fragmented message")
                if opcode == OP_BINARY:
                    raise await self._fail("binary frames are not part of this protocol", 1003)
            else:
                raise await self._fail(f"reserved opcode {opcode:#x}")
            message += payload
            if len(message) > self._max_message_bytes:
                raise await self._fail("message too large", 1009)
            if fin:
                try:
                    return message.decode("utf-8")
                except UnicodeDecodeError:
                    raise await self._fail("invalid UTF-8 in text message", 1007) from None
            expecting_continuation = True

    async def _fail(self, why: str, code: int = 1002) -> WSError:
        await self.close(code, why)
        return WSError(why, code)

    async def _read_frame(self) -> tuple[bool, int, bytes]:
        try:
            head = await self._reader.readexactly(2)
        except (asyncio.IncompleteReadError, ConnectionError) as exc:
            self.closed = True
            raise WSClosed(None, "connection dropped") from exc
        fin = bool(head[0] & 0x80)
        if head[0] & 0x70:
            raise await self._fail("RSV bits set without a negotiated extension")
        opcode = head[0] & 0x0F
        masked = bool(head[1] & 0x80)
        length = head[1] & 0x7F
        if opcode >= OP_CLOSE and (not fin or length > 125):  # control frames
            raise await self._fail("fragmented or oversized control frame")
        if length == 126:
            length = int.from_bytes(await self._reader.readexactly(2), "big")
        elif length == 127:
            length = int.from_bytes(await self._reader.readexactly(8), "big")
        if length > self._max_message_bytes:
            raise await self._fail("frame too large", 1009)
        # RFC 6455 5.1: client frames MUST be masked, server frames MUST NOT.
        if self._mask_outgoing == masked:  # our peer masks iff we don't
            raise await self._fail("peer used the wrong masking mode")
        mask = await self._reader.readexactly(4) if masked else b""
        payload = await self._reader.readexactly(length) if length else b""
        if masked:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        return fin, opcode, payload


async def connect(uri: str) -> WebSocket:
    """Open a client connection to ``ws://host:port/path``."""
    parts = urlsplit(uri)
    if parts.scheme != "ws":
        raise ValueError(f"only ws:// URIs are supported, got {uri!r}")
    host = parts.hostname or "127.0.0.1"
    port = parts.port or 80
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query
    reader, writer = await asyncio.open_connection(host, port)
    key = base64.b64encode(os.urandom(16)).decode()
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    writer.write(request.encode())
    await writer.drain()
    try:
        status = await _read_http_head(reader)
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError) as exc:
        writer.close()
        raise WSError("connection closed during handshake") from exc
    first = status[0]
    if b"101" not in first.split(b"\r\n")[0]:
        writer.close()
        raise WSError(f"handshake rejected: {first.decode('latin1', 'replace').strip()}")
    headers = _parse_headers(status[1])
    if headers.get("sec-websocket-accept") != _accept_value(key):
        writer.close()
        raise WSError("bad Sec-WebSocket-Accept from server")
    return WebSocket(reader, writer, mask_outgoing=True)


async def _read_http_head(reader: asyncio.StreamReader) -> tuple[bytes, bytes]:
    """(status line, header block) of an HTTP message, bounded."""
    raw = await reader.readuntil(b"\r\n\r\n")
    if len(raw) > MAX_HEADER_BYTES:
        raise WSError("HTTP header block too large", 1009)
    line, _, rest = raw.partition(b"\r\n")
    return line + b"\r\n", rest


def _parse_headers(block: bytes) -> dict[str, str]:
    headers: dict[str, str] = {}
    for line in block.split(b"\r\n"):
        if b":" in line:
            name, _, value = line.partition(b":")
            headers[name.strip().decode("latin1").lower()] = value.strip().decode("latin1")
    return headers


class WSServer:
    """Accepts WebSocket upgrades and hands each connection to ``handler``."""

    def __init__(self, handler, *, host: str = "127.0.0.1", port: int = 0) -> None:
        self._handler = handler
        self._host = host
        self._port = port
        self._server: asyncio.Server | None = None

    @property
    def port(self) -> int:
        assert self._server is not None, "server not started"
        return self._server.sockets[0].getsockname()[1]

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._accept, self._host, self._port)

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

    async def _accept(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            head = await asyncio.wait_for(_read_http_head(reader), timeout=10)
        except (
            TimeoutError,
            asyncio.IncompleteReadError,
            asyncio.LimitOverrunError,
            WSError,
        ):
            writer.close()
            return
        request_line, header_block = head
        headers = _parse_headers(header_block)
        key = headers.get("sec-websocket-key")
        path = request_line.split(b" ")[1].decode("latin1") if b" " in request_line else "/"
        if (
            headers.get("upgrade", "").lower() != "websocket"
            or key is None
            or headers.get("sec-websocket-version") != "13"
        ):
            writer.write(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n")
            await writer.drain()
            writer.close()
            return
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {_accept_value(key)}\r\n"
            "\r\n"
        )
        writer.write(response.encode())
        await writer.drain()
        socket_ = WebSocket(reader, writer, mask_outgoing=False)
        try:
            await self._handler(socket_, path)
        except (WSClosed, WSError):
            pass
        finally:
            await socket_.close()
