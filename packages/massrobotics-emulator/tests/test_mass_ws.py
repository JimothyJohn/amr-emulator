"""WebSocket transport tests: RFC 6455 conformance and adversarial peers.

The framing layer is exercised over real sockets (no mocks), and the
adversarial cases speak raw bytes at the server the way an attacker or a
broken client would.
"""

import asyncio
import base64
import hashlib
import os
import secrets

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from massrobotics_emulator import ws

TIMEOUT = 10.0


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, TIMEOUT))


class EchoServer:
    """WSServer echoing text messages back, recording what it saw."""

    def __init__(self):
        self.received: list[str] = []
        self.server = ws.WSServer(self._handle)

    async def _handle(self, socket: ws.WebSocket, path: str) -> None:
        while True:
            text = await socket.receive_text()
            self.received.append(text)
            await socket.send_text(text)

    async def __aenter__(self):
        await self.server.start()
        return self

    async def __aexit__(self, *exc):
        await self.server.stop()


def test_text_roundtrip_and_ping():
    async def scenario():
        async with EchoServer() as echo:
            client = await ws.connect(f"ws://127.0.0.1:{echo.server.port}")
            await client.send_text("hello interop")
            assert await client.receive_text() == "hello interop"
            await client.ping(b"probe")  # pong is consumed transparently
            await client.send_text("after ping")
            assert await client.receive_text() == "after ping"
            await client.close()

    run(scenario())


def test_large_and_unicode_messages_roundtrip():
    async def scenario():
        async with EchoServer() as echo:
            client = await ws.connect(f"ws://127.0.0.1:{echo.server.port}")
            tricky = "\U0001d4ca\U0001d4c3\U0001d4be\U0001d4b8\xf8\u2202\xe9 \u2713 \x00 \uffff"
            for message in [tricky, "x" * 70_000]:
                await client.send_text(message)
                assert await client.receive_text() == message
            await client.close()

    run(scenario())


@settings(max_examples=25, deadline=None)
@given(st.text(max_size=2_000))
def test_any_text_roundtrips(message):
    async def scenario():
        async with EchoServer() as echo:
            client = await ws.connect(f"ws://127.0.0.1:{echo.server.port}")
            await client.send_text(message)
            assert await client.receive_text() == message
            await client.close()

    run(scenario())


async def _raw_upgrade(port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    key = base64.b64encode(os.urandom(16)).decode()
    writer.write(
        (
            f"GET / HTTP/1.1\r\nHost: h\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        ).encode()
    )
    await writer.drain()
    head = await reader.readuntil(b"\r\n\r\n")
    assert b"101" in head.split(b"\r\n", 1)[0]
    expected = base64.b64encode(hashlib.sha1((key + ws._GUID).encode()).digest()).decode()  # noqa: S324
    assert expected.encode() in head
    return reader, writer


def _client_frame(opcode: int, payload: bytes, *, masked: bool = True, fin: bool = True) -> bytes:
    head = bytearray([(0x80 if fin else 0) | opcode])
    mask_bit = 0x80 if masked else 0
    if len(payload) < 126:
        head.append(mask_bit | len(payload))
    else:
        head.append(mask_bit | 126)
        head += len(payload).to_bytes(2, "big")
    if masked:
        mask = secrets.token_bytes(4)
        head += mask
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    return bytes(head) + payload


def _read_close_code(data: bytes) -> int | None:
    # server-to-client frames are unmasked: [0x88, len, code_hi, code_lo, ...]
    if len(data) >= 4 and data[0] == 0x88:
        return int.from_bytes(data[2:4], "big")
    return None


@pytest.mark.parametrize(
    ("frame", "expected_close"),
    [
        # RFC 6455 5.1: unmasked client frame is a protocol error
        (lambda: _client_frame(ws.OP_TEXT, b"naked", masked=False), 1002),
        # binary frames are not part of this protocol
        (lambda: _client_frame(ws.OP_BINARY, b"\x00\x01"), 1003),
        # invalid UTF-8 in a text message
        (lambda: _client_frame(ws.OP_TEXT, b"\xff\xfe\xfd"), 1007),
        # reserved opcode
        (lambda: _client_frame(0x3, b""), 1002),
        # continuation with nothing to continue
        (lambda: _client_frame(ws.OP_CONT, b"orphan"), 1002),
        # fragmented control frame
        (lambda: _client_frame(ws.OP_PING, b"p", fin=False), 1002),
    ],
)
def test_protocol_violations_close_with_correct_code(frame, expected_close):
    async def scenario():
        async with EchoServer() as echo:
            reader, writer = await _raw_upgrade(echo.server.port)
            writer.write(frame())
            await writer.drain()
            data = await reader.read(64)
            assert _read_close_code(data) == expected_close
            writer.close()

    run(scenario())


def test_oversized_message_closes_1009():
    async def scenario():
        async with EchoServer() as echo:
            reader, writer = await _raw_upgrade(echo.server.port)
            huge = ws.MAX_MESSAGE_BYTES + 1
            head = bytearray([0x80 | ws.OP_TEXT, 0x80 | 127])
            head += huge.to_bytes(8, "big")
            head += secrets.token_bytes(4)
            writer.write(bytes(head))  # header alone announces too much
            await writer.drain()
            data = await reader.read(64)
            assert _read_close_code(data) == 1009
            writer.close()

    run(scenario())


def test_fragmented_text_reassembles():
    async def scenario():
        async with EchoServer() as echo:
            reader, writer = await _raw_upgrade(echo.server.port)
            writer.write(_client_frame(ws.OP_TEXT, b"frag", fin=False))
            writer.write(_client_frame(ws.OP_CONT, b"men", fin=False))
            writer.write(_client_frame(ws.OP_CONT, b"ted", fin=True))
            await writer.drain()
            # server echoes the reassembled message as one unmasked text frame
            echoed = await reader.readexactly(2 + len(b"fragmented"))
            assert echoed[0] == 0x80 | ws.OP_TEXT
            assert echoed[2:] == b"fragmented"
            writer.close()

    run(scenario())


def test_non_websocket_request_gets_400():
    async def scenario():
        async with EchoServer() as echo:
            reader, writer = await asyncio.open_connection("127.0.0.1", echo.server.port)
            writer.write(b"GET / HTTP/1.1\r\nHost: h\r\n\r\n")
            await writer.drain()
            head = await reader.readuntil(b"\r\n\r\n")
            assert b"400" in head.split(b"\r\n", 1)[0]
            writer.close()

    run(scenario())


def test_client_rejects_bad_accept_header():
    async def scenario():
        async def imposter(reader, writer):
            await reader.readuntil(b"\r\n\r\n")
            writer.write(
                b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
                b"Connection: Upgrade\r\nSec-WebSocket-Accept: bogus\r\n\r\n"
            )
            await writer.drain()

        server = await asyncio.start_server(imposter, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        with pytest.raises(ws.WSError, match="Accept"):
            await ws.connect(f"ws://127.0.0.1:{port}")
        server.close()
        await server.wait_closed()

    run(scenario())
