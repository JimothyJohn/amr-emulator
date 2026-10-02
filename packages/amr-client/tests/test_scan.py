"""Network discovery of MiR targets — against real sockets, adversarial by default.

Emulator apps are bound to real ephemeral TCP ports (uvicorn), and decoy
servers — a plain HTTP site, a socket that accepts then hangs forever, one
that spews garbage bytes — sit on adjacent ports. The scanner must find
every MiR target and reject every decoy, all under its deadline, so a
hostile or noisy shop-floor network cannot hang or fool it.
"""

from __future__ import annotations

import asyncio
import socket
import threading
import time
from contextlib import closing

import pytest
import uvicorn
from amr_client.scan import (
    DEFAULT_SCAN_PORTS,
    default_candidates,
    expand_hosts,
    local_ipv4,
    scan_network,
    scan_network_async,
)
from amr_emulator.app import create_app
from amr_emulator.fleet import create_fleet_app
from amr_emulator.serverless import build_app

HOST = "127.0.0.1"


def _free_port() -> int:
    with closing(socket.socket()) as sock:
        sock.bind((HOST, 0))
        return sock.getsockname()[1]


class LiveApp:
    """An ASGI app served by uvicorn on a real port for the duration of a test."""

    def __init__(self, app):
        self.port = _free_port()
        config = uvicorn.Config(app, host=HOST, port=self.port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def __enter__(self) -> int:
        self.thread.start()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.server.started:
                return self.port
            time.sleep(0.02)
        raise RuntimeError("uvicorn did not start")

    def __exit__(self, *exc) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=10)


class RawServer:
    """A hostile TCP listener: accepts connections and runs *handler* per socket."""

    def __init__(self, handler):
        self.handler = handler
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, 0))
        self.sock.listen(8)
        self.port = self.sock.getsockname()[1]
        self._stop = False
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def _serve(self) -> None:
        self.sock.settimeout(0.2)
        conns = []
        while not self._stop:
            try:
                conn, _ = self.sock.accept()
            except (TimeoutError, OSError):
                continue
            conns.append(conn)
            threading.Thread(target=self.handler, args=(conn,), daemon=True).start()
        for conn in conns:
            with _silence():
                conn.close()

    def __enter__(self) -> int:
        self.thread.start()
        return self.port

    def __exit__(self, *exc) -> None:
        self._stop = True
        self.thread.join(timeout=5)
        with _silence():
            self.sock.close()


class _silence:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return True  # swallow teardown races on sockets


def _hang_forever(conn) -> None:
    time.sleep(30)  # accept, then never respond — the classic scanner trap


def _spew_garbage(conn) -> None:
    with _silence():
        conn.sendall(b"\x00\xff" * 4096)
        conn.close()


def scan(hosts, ports):
    return scan_network(hosts, ports=ports, connect_timeout=1.0, identify_timeout=3.0)


# --------------------------------------------------------------- host math


def test_expand_hosts_splits_cidr_and_dedups():
    hosts = expand_hosts(["192.168.1.0/30", "mir.local", "192.168.1.1"])
    assert hosts == ["192.168.1.1", "192.168.1.2", "mir.local"]


def test_local_ipv4_is_a_real_address_or_none():
    ip = local_ipv4()
    assert ip is None or ip.count(".") == 3


def test_default_candidates_are_a_24():
    candidates = default_candidates()
    assert candidates == [] or len(candidates) == 254


def test_default_scan_ports_cover_real_and_emulator():
    assert 80 in DEFAULT_SCAN_PORTS and 8080 in DEFAULT_SCAN_PORTS


# --------------------------------------------------------------- finds MiR


def test_finds_a_robot_on_its_port():
    with LiveApp(create_app("3.8.1")) as port:
        found = scan([HOST], [port])
    assert len(found) == 1
    assert found[0].info.kind == "robot"
    assert found[0].info.version == "3.8.1"
    assert found[0].url == f"http://{HOST}:{port}"


def test_finds_a_fleet_and_a_robot_across_ports():
    with LiveApp(create_app("2.14.7")) as rport, LiveApp(create_fleet_app("1.5.0")) as fport:
        found = scan([HOST], [rport, fport])
    by_kind = {s.info.kind: s for s in found}
    assert by_kind["robot"].info.version == "2.14.7"
    assert by_kind["fleet"].info.version == "1.5.0"


def test_finds_the_multi_version_dispatcher():
    with LiveApp(build_app()) as port:
        found = scan([HOST], [port])
    assert len(found) == 1
    assert found[0].info.kind == "dispatcher"
    assert found[0].info.versions


# ------------------------------------------------------- rejects the noise


def test_ignores_a_non_mir_http_server():
    class Hello:
        async def __call__(self, scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b'{"hello":"world"}'})

    with LiveApp(Hello()) as port:
        assert scan([HOST], [port]) == []


def test_a_hanging_socket_cannot_stall_the_sweep():
    with RawServer(_hang_forever) as hport, LiveApp(create_app("3.8.1")) as rport:
        start = time.monotonic()
        found = scan([HOST], [hport, rport])
        elapsed = time.monotonic() - start
    # The robot is still found, and the hung port is cut off by the deadline
    # rather than blocking — well under the 30s the handler would sleep.
    assert [s.info.kind for s in found] == ["robot"]
    assert elapsed < 15


def test_garbage_bytes_do_not_crash_the_scan():
    with RawServer(_spew_garbage) as gport, LiveApp(create_fleet_app("1.5.0")) as fport:
        found = scan([HOST], [gport, fport])
    assert [s.info.kind for s in found] == ["fleet"]


def test_closed_ports_yield_nothing():
    dead = _free_port()  # nothing is listening here
    assert scan([HOST], [dead]) == []


# ------------------------------------------------------------- guardrails


def test_empty_host_list_is_an_error():
    with pytest.raises(ValueError, match="no hosts to scan"):
        scan_network([], ports=[80])


def test_oversized_sweep_is_refused():
    with pytest.raises(ValueError, match="exceeds"):
        scan_network(["10.0.0.0/16"], ports=[80])


def test_async_and_sync_agree():
    with LiveApp(create_app("3.8.1")) as port:
        sync_found = scan([HOST], [port])
        async_found = asyncio.run(
            scan_network_async([HOST], ports=[port], connect_timeout=1.0, identify_timeout=3.0)
        )
    assert [s.url for s in sync_found] == [s.url for s in async_found]
