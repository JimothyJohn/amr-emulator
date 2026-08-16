"""MQTT 3.1.1 packet codec — pure encode/decode, no sockets.

This is the adversarial surface of the embedded broker: `decode_body` and
`read_packet` consume attacker-controlled bytes, so every malformed input
must raise ``MQTTError`` (never ``IndexError``/``UnicodeDecodeError``/hangs).
QoS 2 packets (PUBREC/PUBREL/PUBCOMP) are deliberately not implemented; the
broker refuses QoS 2 publishes by closing the connection. Remaining-length
values must use the minimal encoding, per the spec's algorithm.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

CONNECT = 1
CONNACK = 2
PUBLISH = 3
PUBACK = 4
SUBSCRIBE = 8
SUBACK = 9
UNSUBSCRIBE = 10
UNSUBACK = 11
PINGREQ = 12
PINGRESP = 13
DISCONNECT = 14

PROTOCOL_NAME = "MQTT"
PROTOCOL_LEVEL = 4  # MQTT 3.1.1

CONNACK_ACCEPTED = 0
CONNACK_REFUSED_PROTOCOL = 1
CONNACK_REFUSED_IDENTIFIER = 2
CONNACK_REFUSED_BAD_CREDENTIALS = 4
CONNACK_REFUSED_NOT_AUTHORIZED = 5

SUBACK_FAILURE = 0x80

MAX_REMAINING_LENGTH = 268_435_455


class MQTTError(Exception):
    """Malformed packet, protocol violation, or client-side operation failure."""


@dataclass(frozen=True)
class Message:
    """An application message as seen by publishers and subscribers."""

    topic: str
    payload: bytes
    qos: int = 0
    retain: bool = False


@dataclass(frozen=True)
class Connect:
    client_id: str
    keepalive: int = 60
    clean_session: bool = True
    will_topic: str | None = None
    will_payload: bytes = b""
    will_qos: int = 0
    will_retain: bool = False
    username: str | None = None
    password: bytes | None = None


@dataclass(frozen=True)
class ConnAck:
    return_code: int
    session_present: bool = False


@dataclass(frozen=True)
class Publish:
    topic: str
    payload: bytes
    qos: int = 0
    retain: bool = False
    dup: bool = False
    packet_id: int | None = None


@dataclass(frozen=True)
class PubAck:
    packet_id: int


@dataclass(frozen=True)
class Subscribe:
    packet_id: int
    topics: tuple[tuple[str, int], ...]  # (filter, requested qos)


@dataclass(frozen=True)
class SubAck:
    packet_id: int
    return_codes: tuple[int, ...]


@dataclass(frozen=True)
class Unsubscribe:
    packet_id: int
    topics: tuple[str, ...]


@dataclass(frozen=True)
class UnsubAck:
    packet_id: int


@dataclass(frozen=True)
class PingReq:
    pass


@dataclass(frozen=True)
class PingResp:
    pass


@dataclass(frozen=True)
class Disconnect:
    pass


Packet = (
    Connect
    | ConnAck
    | Publish
    | PubAck
    | Subscribe
    | SubAck
    | Unsubscribe
    | UnsubAck
    | PingReq
    | PingResp
    | Disconnect
)


@dataclass
class _Reader:
    """Bounds-checked cursor over a packet body."""

    data: bytes
    pos: int = 0
    _len: int = field(init=False)

    def __post_init__(self) -> None:
        self._len = len(self.data)

    def take(self, n: int) -> bytes:
        if n < 0 or self.pos + n > self._len:
            raise MQTTError("packet truncated")
        chunk = self.data[self.pos : self.pos + n]
        self.pos += n
        return chunk

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        chunk = self.take(2)
        return (chunk[0] << 8) | chunk[1]

    def string(self) -> str:
        raw = self.take(self.u16())
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise MQTTError("invalid UTF-8 string") from exc
        if "\x00" in text:
            raise MQTTError("U+0000 in string")
        return text

    def binary(self) -> bytes:
        return self.take(self.u16())

    def rest(self) -> bytes:
        chunk = self.data[self.pos :]
        self.pos = self._len
        return chunk

    def done(self) -> None:
        if self.pos != self._len:
            raise MQTTError("trailing bytes in packet")


def _string(text: str) -> bytes:
    raw = text.encode("utf-8")
    if len(raw) > 0xFFFF:
        raise MQTTError("string too long")
    return len(raw).to_bytes(2, "big") + raw


def _binary(raw: bytes) -> bytes:
    if len(raw) > 0xFFFF:
        raise MQTTError("binary field too long")
    return len(raw).to_bytes(2, "big") + raw


def encode_remaining_length(value: int) -> bytes:
    if value < 0 or value > MAX_REMAINING_LENGTH:
        raise MQTTError("remaining length out of range")
    out = bytearray()
    while True:
        value, digit = divmod(value, 128)
        out.append(digit | (0x80 if value else 0))
        if not value:
            return bytes(out)


def decode_remaining_length(data: bytes) -> tuple[int, int]:
    """Return (value, bytes consumed). Rejects overlong and >4-byte encodings."""
    value = 0
    for i in range(4):
        if i >= len(data):
            raise MQTTError("remaining length truncated")
        digit = data[i]
        value |= (digit & 0x7F) << (7 * i)
        if not digit & 0x80:
            if i > 0 and digit == 0:
                raise MQTTError("overlong remaining length")
            return value, i + 1
    raise MQTTError("remaining length exceeds 4 bytes")


def _packet_id(value: int) -> int:
    if not 1 <= value <= 0xFFFF:
        raise MQTTError("invalid packet id")
    return value


def encode(packet: Packet) -> bytes:
    type_flags, body = _encode_body(packet)
    return bytes([type_flags]) + encode_remaining_length(len(body)) + body


def _encode_body(packet: Packet) -> tuple[int, bytes]:
    match packet:
        case Connect():
            flags = 0x02 if packet.clean_session else 0x00
            payload = _string(packet.client_id)
            if packet.will_topic is not None:
                if not 0 <= packet.will_qos <= 2:
                    raise MQTTError("invalid will qos")
                flags |= 0x04 | (packet.will_qos << 3) | (0x20 if packet.will_retain else 0)
                payload += _string(packet.will_topic) + _binary(packet.will_payload)
            if packet.username is not None:
                flags |= 0x80
                payload += _string(packet.username)
                if packet.password is not None:
                    flags |= 0x40
                    payload += _binary(packet.password)
            elif packet.password is not None:
                raise MQTTError("password requires username")
            head = (
                _string(PROTOCOL_NAME)
                + bytes([PROTOCOL_LEVEL, flags])
                + packet.keepalive.to_bytes(2, "big")
            )
            return CONNECT << 4, head + payload
        case ConnAck():
            return CONNACK << 4, bytes([1 if packet.session_present else 0, packet.return_code])
        case Publish():
            if not 0 <= packet.qos <= 1:
                raise MQTTError("unsupported publish qos")
            validate_topic(packet.topic)
            flags = (0x08 if packet.dup else 0) | (packet.qos << 1) | (1 if packet.retain else 0)
            body = _string(packet.topic)
            if packet.qos:
                if packet.packet_id is None:
                    raise MQTTError("qos>0 publish requires packet id")
                body += _packet_id(packet.packet_id).to_bytes(2, "big")
            return (PUBLISH << 4) | flags, body + packet.payload
        case PubAck():
            return PUBACK << 4, _packet_id(packet.packet_id).to_bytes(2, "big")
        case Subscribe():
            if not packet.topics:
                raise MQTTError("empty subscribe")
            body = _packet_id(packet.packet_id).to_bytes(2, "big")
            for topic_filter, qos in packet.topics:
                if not 0 <= qos <= 2:
                    raise MQTTError("invalid subscribe qos")
                body += _string(topic_filter) + bytes([qos])
            return (SUBSCRIBE << 4) | 0x02, body
        case SubAck():
            return (
                SUBACK << 4,
                _packet_id(packet.packet_id).to_bytes(2, "big") + bytes(packet.return_codes),
            )
        case Unsubscribe():
            if not packet.topics:
                raise MQTTError("empty unsubscribe")
            body = _packet_id(packet.packet_id).to_bytes(2, "big")
            for topic_filter in packet.topics:
                body += _string(topic_filter)
            return (UNSUBSCRIBE << 4) | 0x02, body
        case UnsubAck():
            return UNSUBACK << 4, _packet_id(packet.packet_id).to_bytes(2, "big")
        case PingReq():
            return PINGREQ << 4, b""
        case PingResp():
            return PINGRESP << 4, b""
        case Disconnect():
            return DISCONNECT << 4, b""
    raise MQTTError(f"cannot encode {type(packet).__name__}")


def decode_body(first_byte: int, body: bytes) -> Packet:
    packet_type = first_byte >> 4
    flags = first_byte & 0x0F
    reader = _Reader(body)
    match packet_type:
        case x if x == CONNECT:
            return _decode_connect(flags, reader)
        case x if x == CONNACK:
            _require_flags(flags, 0)
            ack_flags, return_code = reader.u8(), reader.u8()
            if ack_flags & 0xFE:
                raise MQTTError("invalid connack flags")
            reader.done()
            return ConnAck(return_code=return_code, session_present=bool(ack_flags & 1))
        case x if x == PUBLISH:
            return _decode_publish(flags, reader)
        case x if x == PUBACK:
            _require_flags(flags, 0)
            packet = PubAck(packet_id=_packet_id(reader.u16()))
            reader.done()
            return packet
        case x if x == SUBSCRIBE:
            _require_flags(flags, 0x02)
            packet_id = _packet_id(reader.u16())
            topics: list[tuple[str, int]] = []
            while reader.pos != len(body):
                topic_filter = reader.string()
                qos = reader.u8()
                if qos > 2:
                    raise MQTTError("invalid subscribe qos")
                validate_filter(topic_filter)
                topics.append((topic_filter, qos))
            if not topics:
                raise MQTTError("empty subscribe")
            return Subscribe(packet_id=packet_id, topics=tuple(topics))
        case x if x == SUBACK:
            _require_flags(flags, 0)
            packet_id = _packet_id(reader.u16())
            codes = reader.rest()
            if not codes:
                raise MQTTError("empty suback")
            return SubAck(packet_id=packet_id, return_codes=tuple(codes))
        case x if x == UNSUBSCRIBE:
            _require_flags(flags, 0x02)
            packet_id = _packet_id(reader.u16())
            filters: list[str] = []
            while reader.pos != len(body):
                topic_filter = reader.string()
                validate_filter(topic_filter)
                filters.append(topic_filter)
            if not filters:
                raise MQTTError("empty unsubscribe")
            return Unsubscribe(packet_id=packet_id, topics=tuple(filters))
        case x if x == UNSUBACK:
            _require_flags(flags, 0)
            packet = UnsubAck(packet_id=_packet_id(reader.u16()))
            reader.done()
            return packet
        case x if x == PINGREQ:
            _require_flags(flags, 0)
            reader.done()
            return PingReq()
        case x if x == PINGRESP:
            _require_flags(flags, 0)
            reader.done()
            return PingResp()
        case x if x == DISCONNECT:
            _require_flags(flags, 0)
            reader.done()
            return Disconnect()
    raise MQTTError(f"unsupported packet type {packet_type}")


def _require_flags(flags: int, expected: int) -> None:
    if flags != expected:
        raise MQTTError("invalid fixed-header flags")


def _decode_connect(flags: int, reader: _Reader) -> Connect:
    _require_flags(flags, 0)
    if reader.string() != PROTOCOL_NAME:
        raise MQTTError("unknown protocol name")
    if reader.u8() != PROTOCOL_LEVEL:
        # Handled by the broker as CONNACK rc=1; decode still fails loudly.
        raise UnsupportedProtocolLevel("unsupported protocol level")
    connect_flags = reader.u8()
    if connect_flags & 0x01:
        raise MQTTError("reserved connect flag set")
    keepalive = reader.u16()
    client_id = reader.string()
    will_topic: str | None = None
    will_payload = b""
    will_qos = (connect_flags >> 3) & 0x03
    will_retain = bool(connect_flags & 0x20)
    if connect_flags & 0x04:
        if will_qos > 2:
            raise MQTTError("invalid will qos")
        will_topic = reader.string()
        validate_topic(will_topic)
        will_payload = reader.binary()
    elif will_qos or will_retain:
        raise MQTTError("will flags without will")
    username: str | None = None
    password: bytes | None = None
    if connect_flags & 0x80:
        username = reader.string()
    if connect_flags & 0x40:
        if username is None:
            raise MQTTError("password requires username")
        password = reader.binary()
    reader.done()
    return Connect(
        client_id=client_id,
        keepalive=keepalive,
        clean_session=bool(connect_flags & 0x02),
        will_topic=will_topic,
        will_payload=will_payload,
        will_qos=will_qos if will_topic is not None else 0,
        will_retain=will_retain if will_topic is not None else False,
        username=username,
        password=password,
    )


def _decode_publish(flags: int, reader: _Reader) -> Publish:
    qos = (flags >> 1) & 0x03
    if qos == 3:
        raise MQTTError("invalid publish qos")
    if qos == 2:
        raise MQTTError("qos 2 not supported")
    topic = reader.string()
    validate_topic(topic)
    packet_id = _packet_id(reader.u16()) if qos else None
    return Publish(
        topic=topic,
        payload=reader.rest(),
        qos=qos,
        retain=bool(flags & 0x01),
        dup=bool(flags & 0x08),
        packet_id=packet_id,
    )


class UnsupportedProtocolLevel(MQTTError):
    """CONNECT with a protocol level other than 4 — answered with CONNACK rc=1."""


def validate_topic(topic: str) -> None:
    """A publish topic: non-empty, no wildcards."""
    if not topic:
        raise MQTTError("empty topic")
    if "+" in topic or "#" in topic:
        raise MQTTError("wildcard in publish topic")


def validate_filter(topic_filter: str) -> None:
    """A subscription filter: non-empty; '#' only as final level; '+' alone in its level."""
    if not topic_filter:
        raise MQTTError("empty topic filter")
    levels = topic_filter.split("/")
    for i, level in enumerate(levels):
        if "#" in level and (level != "#" or i != len(levels) - 1):
            raise MQTTError("invalid '#' placement in filter")
        if "+" in level and level != "+":
            raise MQTTError("invalid '+' placement in filter")


def topic_matches(topic_filter: str, topic: str) -> bool:
    """MQTT 3.1.1 matching; wildcards never match a leading-'$' first level."""
    filter_levels = topic_filter.split("/")
    topic_levels = topic.split("/")
    if topic_levels[0].startswith("$") and filter_levels[0] in ("+", "#"):
        return False
    for i, level in enumerate(filter_levels):
        if level == "#":
            return True
        if i >= len(topic_levels):
            return False
        if level != "+" and level != topic_levels[i]:
            return False
    return len(filter_levels) == len(topic_levels)


async def read_packet(
    read: Callable[[int], Awaitable[bytes]], max_packet_size: int = 1_048_576
) -> Packet:
    """Read one packet from a transport-agnostic `read(n) -> exactly n bytes` callable.

    The callable shall raise (e.g. ``asyncio.IncompleteReadError``) on EOF.
    """
    first = (await read(1))[0]
    length_bytes = b""
    for _ in range(4):
        length_bytes += await read(1)
        if not length_bytes[-1] & 0x80:
            break
    remaining, _consumed = decode_remaining_length(length_bytes)
    if remaining + len(length_bytes) + 1 > max_packet_size:
        raise MQTTError("packet exceeds maximum size")
    body = await read(remaining) if remaining else b""
    return decode_body(first, body)
