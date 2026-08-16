"""Codec round-trips and adversarial decoding for the embedded MQTT stack."""

import asyncio

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from vda5050_emulator.mqtt import codec
from vda5050_emulator.mqtt.codec import MQTTError

ROUND_TRIP_PACKETS = [
    codec.Connect(client_id="agv-1"),
    codec.Connect(
        client_id="agv-2",
        keepalive=5,
        clean_session=True,
        will_topic="uagv/v3/kit/0001/connection",
        will_payload=b'{"connectionState":"CONNECTION_BROKEN"}',
        will_qos=1,
        will_retain=True,
        username="robot",
        password=b"secret",
    ),
    codec.ConnAck(return_code=0),
    codec.ConnAck(return_code=5, session_present=False),
    codec.Publish(topic="a/b", payload=b"x" * 300),
    codec.Publish(topic="a/b", payload=b"", qos=1, retain=True, packet_id=7),
    codec.Publish(topic="a", payload=b"p", qos=1, dup=True, packet_id=0xFFFF),
    codec.PubAck(packet_id=1),
    codec.Subscribe(packet_id=2, topics=(("uagv/v3/+/+/state", 0), ("#", 1))),
    codec.SubAck(packet_id=2, return_codes=(0, 1)),
    codec.SubAck(packet_id=3, return_codes=(0x80,)),
    codec.Unsubscribe(packet_id=4, topics=("a/b", "c/#")),
    codec.UnsubAck(packet_id=4),
    codec.PingReq(),
    codec.PingResp(),
    codec.Disconnect(),
]


@pytest.mark.parametrize("packet", ROUND_TRIP_PACKETS, ids=lambda p: type(p).__name__)
def test_round_trip(packet):
    encoded = codec.encode(packet)
    first, rest = encoded[0], encoded[1:]
    length, consumed = codec.decode_remaining_length(rest)
    body = rest[consumed:]
    assert len(body) == length
    assert codec.decode_body(first, body) == packet


@pytest.mark.parametrize(
    ("value", "encoded"),
    [
        (0, b"\x00"),
        (127, b"\x7f"),
        (128, b"\x80\x01"),
        (16_383, b"\xff\x7f"),
        (16_384, b"\x80\x80\x01"),
        (2_097_151, b"\xff\xff\x7f"),
        (2_097_152, b"\x80\x80\x80\x01"),
        (268_435_455, b"\xff\xff\xff\x7f"),
    ],
)
def test_remaining_length_boundaries(value, encoded):
    assert codec.encode_remaining_length(value) == encoded
    assert codec.decode_remaining_length(encoded) == (value, len(encoded))


@pytest.mark.parametrize(
    "bad",
    [b"", b"\x80", b"\x80\x80\x80\x80", b"\x80\x00", b"\x80\x80\x00", b"\xff\xff\xff\xff"],
)
def test_remaining_length_rejects(bad):
    with pytest.raises(MQTTError):
        codec.decode_remaining_length(bad)


def test_remaining_length_range():
    with pytest.raises(MQTTError):
        codec.encode_remaining_length(codec.MAX_REMAINING_LENGTH + 1)
    with pytest.raises(MQTTError):
        codec.encode_remaining_length(-1)


@pytest.mark.parametrize(
    "packet",
    [
        codec.Publish(topic="", payload=b""),
        codec.Publish(topic="a/+/b", payload=b""),
        codec.Publish(topic="a/#", payload=b""),
        codec.Publish(topic="a", payload=b"", qos=2, packet_id=1),
        codec.Publish(topic="a", payload=b"", qos=1),  # missing packet id
        codec.Subscribe(packet_id=1, topics=()),
        codec.Subscribe(packet_id=0, topics=(("a", 0),)),
        codec.Unsubscribe(packet_id=1, topics=()),
        codec.Connect(client_id="x", password=b"pw-without-username"),
    ],
    ids=repr,
)
def test_encode_rejects_invalid(packet):
    with pytest.raises(MQTTError):
        codec.encode(packet)


@pytest.mark.parametrize(
    ("first", "body"),
    [
        (0x10, b""),  # truncated CONNECT
        (0x13, b""),  # CONNECT with reserved flags
        (0x60, b""),  # PUBREL (qos2) unsupported
        (0x00, b""),  # reserved packet type 0
        (0xF0, b""),  # reserved packet type 15
        (0x36, b"\x00\x01a"),  # PUBLISH qos=3
        (0x34, b"\x00\x01a\x00\x00"),  # qos1 with packet id 0
        (0x30, b"\x00\x03a\xff\xfe"),  # invalid UTF-8 topic
        (0x30, b"\x00\x03a\x00b"),  # U+0000 in topic
        (0x82, b"\x00\x01\x00\x05a/#/b\x00"),  # filter with '#' before the final level
        (0x82, b"\x00\x01"),  # SUBSCRIBE with no topics
        (0x80, b"\x00\x01\x00\x01a\x00"),  # SUBSCRIBE with wrong fixed flags
        (0x20, b"\x04\x00"),  # CONNACK with invalid ack flags
        (0xC0, b"\x00"),  # PINGREQ with a body
    ],
)
def test_decode_rejects_malformed(first, body):
    with pytest.raises(MQTTError):
        codec.decode_body(first, body)


def test_decode_rejects_bad_filter_placement():
    for bad_filter in ("a/#/b", "#/a", "a+/b", "a/b+", ""):
        with pytest.raises(MQTTError):
            codec.validate_filter(bad_filter)


def test_connect_protocol_level_is_distinct_error():
    good = codec.encode(codec.Connect(client_id="x"))
    level_index = good.index(b"MQTT") + 4
    bad = good[:level_index] + bytes([3]) + good[level_index + 1 :]
    with pytest.raises(codec.UnsupportedProtocolLevel):
        codec.decode_body(bad[0], bad[2:])


@pytest.mark.parametrize(
    ("topic_filter", "topic", "expected"),
    [
        ("a/b", "a/b", True),
        ("a/b", "a/b/c", False),
        ("a/+", "a/b", True),
        ("a/+", "a", False),
        ("+/b", "a/b", True),
        ("#", "a/b/c", True),
        ("a/#", "a", True),
        ("a/#", "a/b/c", True),
        ("a/#", "b/a", False),
        ("+/+", "a/b", True),
        ("#", "$SYS/x", False),
        ("+/x", "$SYS/x", False),
        ("$SYS/#", "$SYS/x", True),
        ("uagv/v3/+/+/state", "uagv/v3/kit/0001/state", True),
        ("uagv/v3/+/+/state", "uagv/v3/kit/0001/order", False),
    ],
)
def test_topic_matching(topic_filter, topic, expected):
    assert codec.topic_matches(topic_filter, topic) is expected


@given(first=st.integers(min_value=0, max_value=255), body=st.binary(max_size=512))
@settings(max_examples=400, deadline=None)
def test_fuzz_decode_body_never_crashes(first, body):
    try:
        packet = codec.decode_body(first, body)
    except MQTTError:
        return
    assert isinstance(packet, codec.Packet)


@given(data=st.binary(min_size=1, max_size=512))
@settings(max_examples=400, deadline=None)
def test_fuzz_read_packet_never_crashes(data):
    async def run() -> None:
        view = memoryview(bytes(data))
        pos = 0

        async def read(n: int) -> bytes:
            nonlocal pos
            if pos + n > len(view):
                raise asyncio.IncompleteReadError(bytes(view[pos:]), pos + n)
            chunk = bytes(view[pos : pos + n])
            pos += n
            return chunk

        try:
            packet = await codec.read_packet(read, max_packet_size=1024)
            assert isinstance(packet, codec.Packet)
        except (MQTTError, asyncio.IncompleteReadError):
            pass

    asyncio.run(run())
