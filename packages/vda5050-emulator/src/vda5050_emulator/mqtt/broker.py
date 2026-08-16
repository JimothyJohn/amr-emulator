"""Embedded asyncio MQTT 3.1.1 broker.

Purpose-built for the VDA5050 emulator: QoS 0/1, retained messages, last
wills, wildcard subscriptions, optional username/password — and nothing else
(no QoS 2, no persistent sessions; every session is treated as clean).
QoS 1 outbound is sent with a packet id but not retransmitted: delivery runs
over local, reliable TCP and the emulator's own state topic is periodically
republished anyway.

A parse error, oversized packet, or keepalive timeout kills only the one
offending connection (its last will fires); the broker itself must survive
arbitrary garbage bytes.
"""

from __future__ import annotations

import asyncio
import itertools
import logging
from contextlib import suppress

from vda5050_emulator.mqtt import codec
from vda5050_emulator.mqtt.codec import Message, MQTTError

log = logging.getLogger(__name__)

_CONNECT_TIMEOUT_S = 10.0


class _Session:
    def __init__(
        self, client_id: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self.client_id = client_id
        self.reader = reader
        self.writer = writer
        self.subscriptions: dict[str, int] = {}
        self.will: Message | None = None
        self.keepalive = 0
        self.write_lock = asyncio.Lock()
        self.closed = asyncio.Event()

    async def send(self, packet: codec.Packet) -> None:
        data = codec.encode(packet)
        async with self.write_lock:
            self.writer.write(data)
            await self.writer.drain()


class Broker:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        *,
        username: str | None = None,
        password: str | None = None,
        max_packet_size: int = 1_048_576,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._max_packet_size = max_packet_size
        self._server: asyncio.Server | None = None
        self._sessions: dict[str, _Session] = {}
        self._retained: dict[str, Message] = {}
        self._packet_ids = itertools.cycle(range(1, 0x10000))
        self._auto_ids = itertools.count(1)
        self._conn_tasks: set[asyncio.Task] = set()

    @property
    def port(self) -> int:
        if self._server is None:
            raise RuntimeError("broker not started")
        return self._server.sockets[0].getsockname()[1]

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle_connection, self._host, self._port)

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        # Broker shutdown is not a client failure: close without firing wills.
        for session in list(self._sessions.values()):
            session.will = None
            self._close_transport(session)
        for task in list(self._conn_tasks):
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        self._sessions.clear()

    async def disconnect_client(self, client_id: str) -> bool:
        """Abruptly sever a client's connection (no DISCONNECT) so its will fires."""
        session = self._sessions.get(client_id)
        if session is None:
            return False
        await self._abort(session)
        return True

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        task = asyncio.current_task()
        assert task is not None
        self._conn_tasks.add(task)
        session: _Session | None = None
        try:
            session = await self._perform_handshake(reader, writer)
            if session is None:
                return
            await self._serve(session)
        except (MQTTError, asyncio.IncompleteReadError, ConnectionError, TimeoutError):
            if session is not None:
                await self._abort(session)
        finally:
            if session is not None and self._sessions.get(session.client_id) is session:
                del self._sessions[session.client_id]
            self._close_writer(writer)
            self._conn_tasks.discard(task)

    async def _perform_handshake(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> _Session | None:
        try:
            async with asyncio.timeout(_CONNECT_TIMEOUT_S):
                packet = await codec.read_packet(reader.readexactly, self._max_packet_size)
        except codec.UnsupportedProtocolLevel:
            with suppress(ConnectionError):
                writer.write(codec.encode(codec.ConnAck(codec.CONNACK_REFUSED_PROTOCOL)))
                await writer.drain()
            return None
        except (MQTTError, asyncio.IncompleteReadError, ConnectionError, TimeoutError):
            return None
        if not isinstance(packet, codec.Connect):
            return None
        if self._username is not None and (
            packet.username != self._username or packet.password != (self._password or "").encode()
        ):
            with suppress(ConnectionError):
                writer.write(codec.encode(codec.ConnAck(codec.CONNACK_REFUSED_BAD_CREDENTIALS)))
                await writer.drain()
            return None
        client_id = packet.client_id or f"auto-{next(self._auto_ids)}"
        previous = self._sessions.get(client_id)
        if previous is not None:
            await self._abort(previous)  # session takeover: old will fires
        session = _Session(client_id, reader, writer)
        if packet.will_topic is not None:
            session.will = Message(
                topic=packet.will_topic,
                payload=packet.will_payload,
                qos=min(packet.will_qos, 1),
                retain=packet.will_retain,
            )
        session.keepalive = packet.keepalive
        self._sessions[client_id] = session
        await session.send(codec.ConnAck(codec.CONNACK_ACCEPTED))
        return session

    async def _serve(self, session: _Session) -> None:
        timeout = session.keepalive * 1.5 if session.keepalive else None
        while True:
            try:
                async with asyncio.timeout(timeout):
                    packet = await codec.read_packet(
                        session.reader.readexactly, self._max_packet_size
                    )
            except TimeoutError:
                await self._abort(session)
                return
            match packet:
                case codec.Publish():
                    await self._on_publish(session, packet)
                case codec.Subscribe():
                    await self._on_subscribe(session, packet)
                case codec.Unsubscribe():
                    for topic_filter in packet.topics:
                        session.subscriptions.pop(topic_filter, None)
                    await session.send(codec.UnsubAck(packet_id=packet.packet_id))
                case codec.PubAck():
                    pass  # ack for a QoS 1 delivery we made; nothing tracked (see module doc)
                case codec.PingReq():
                    await session.send(codec.PingResp())
                case codec.Disconnect():
                    session.will = None
                    self._close_transport(session)
                    return
                case _:
                    raise MQTTError(f"unexpected {type(packet).__name__} from client")

    async def _on_publish(self, session: _Session, packet: codec.Publish) -> None:
        message = Message(
            topic=packet.topic, payload=packet.payload, qos=packet.qos, retain=packet.retain
        )
        if packet.qos and packet.packet_id is not None:
            await session.send(codec.PubAck(packet_id=packet.packet_id))
        await self._route(message)

    async def _on_subscribe(self, session: _Session, packet: codec.Subscribe) -> None:
        granted: list[int] = []
        for topic_filter, requested_qos in packet.topics:
            qos = min(requested_qos, 1)
            session.subscriptions[topic_filter] = qos
            granted.append(qos)
        await session.send(codec.SubAck(packet_id=packet.packet_id, return_codes=tuple(granted)))
        for topic_filter, _requested in packet.topics:
            for topic, retained in list(self._retained.items()):
                if codec.topic_matches(topic_filter, topic):
                    await self._deliver(session, retained, retain=True)

    async def _route(self, message: Message) -> None:
        if message.retain:
            if message.payload:
                self._retained[message.topic] = message
            else:
                self._retained.pop(message.topic, None)
        for session in list(self._sessions.values()):
            if any(codec.topic_matches(f, message.topic) for f in session.subscriptions):
                await self._deliver(session, message, retain=False)

    async def _deliver(self, session: _Session, message: Message, *, retain: bool) -> None:
        qos = min(
            message.qos,
            max(
                (
                    q
                    for f, q in session.subscriptions.items()
                    if codec.topic_matches(f, message.topic)
                ),
                default=0,
            ),
        )
        publish = codec.Publish(
            topic=message.topic,
            payload=message.payload,
            qos=qos,
            retain=retain,
            packet_id=next(self._packet_ids) if qos else None,
        )
        try:
            await session.send(publish)
        except (ConnectionError, RuntimeError):
            await self._abort(session)

    async def _abort(self, session: _Session) -> None:
        """Abnormal termination: fire the last will, then drop the connection."""
        if self._sessions.get(session.client_id) is session:
            del self._sessions[session.client_id]
        will, session.will = session.will, None
        self._close_transport(session)
        if will is not None:
            await self._route(will)

    def _close_transport(self, session: _Session) -> None:
        if not session.closed.is_set():
            session.closed.set()
            self._close_writer(session.writer)

    def _close_writer(self, writer: asyncio.StreamWriter) -> None:
        with suppress(ConnectionError, RuntimeError):
            writer.close()
