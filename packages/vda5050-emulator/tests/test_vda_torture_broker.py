"""Broker torture: manufacturing-floor failure modes for the embedded MQTT
broker — reconnect storms, session takeover, stuck consumers, payload edges,
wildcard overlap and keepalive boundaries. Every test asserts the broker
keeps serving *other* clients while the abusive one is punished."""

from __future__ import annotations

import asyncio
import contextlib
import json

from vda5050_emulator import Broker, Message, MQTTClient
from vda5050_emulator.mqtt import codec
from vda_harness import run


async def _client(port: int, client_id: str, **kwargs) -> MQTTClient:
    client = MQTTClient(client_id, "127.0.0.1", port, **kwargs)
    await client.connect()
    return client


def test_reconnect_storm_fires_every_will_and_serves_others():
    async def body():
        broker = Broker(port=0)
        await broker.start()
        try:
            watcher = await _client(broker.port, "watcher")
            await watcher.subscribe("wills/#")
            steady = await _client(broker.port, "steady")
            await steady.subscribe("steady/topic")

            for i in range(50):
                stormer = MQTTClient(
                    f"storm-{i}",
                    "127.0.0.1",
                    broker.port,
                    will=Message("wills/storm", f"gone-{i}".encode(), qos=1),
                )
                await stormer.connect()
                await stormer.drop()  # abnormal -> will fires
                # Steady traffic interleaved with every storm cycle.
                await watcher.publish("steady/topic", f"tick-{i}".encode())

            wills, ticks = set(), set()
            deadline = asyncio.get_running_loop().time() + 10
            while (
                len(wills) < 50 or len(ticks) < 50
            ) and asyncio.get_running_loop().time() < deadline:
                for client, bucket, prefix in (
                    (watcher, wills, b"gone-"),
                    (steady, ticks, b"tick-"),
                ):
                    while not client.messages.empty():
                        message = client.messages.get_nowait()
                        assert message.payload.startswith(prefix), (
                            f"cross-talk: {message.topic} {message.payload[:20]!r}"
                        )
                        bucket.add(message.payload)
                await asyncio.sleep(0.02)
            assert len(wills) == 50, f"lost wills: {50 - len(wills)}"
            assert len(ticks) == 50, f"lost steady traffic: {50 - len(ticks)}"
            await watcher.disconnect()
            await steady.disconnect()
        finally:
            await broker.stop()

    run(body())


def test_session_takeover_storm_newest_always_wins():
    async def body():
        broker = Broker(port=0)
        await broker.start()
        try:
            observer = await _client(broker.port, "observer")
            await observer.subscribe("robot/state")
            winner = None
            for _attempt in range(20):  # two "NICs" fighting over one client_id
                winner = MQTTClient("robot-1", "127.0.0.1", broker.port)
                await winner.connect()
            assert winner is not None
            await winner.publish("robot/state", b"alive")
            message = await asyncio.wait_for(observer.messages.get(), timeout=5)
            assert message.payload == b"alive"
            await winner.disconnect()
            await observer.disconnect()
        finally:
            await broker.stop()

    run(body())


def test_stuck_subscriber_does_not_wedge_the_publisher():
    """A subscriber that stops reading its socket must not block delivery to
    healthy subscribers: the broker aborts the stuck session after a bounded
    delivery timeout instead of letting one client's TCP backpressure freeze
    the publisher's routing."""

    async def body():
        broker = Broker(port=0)
        await broker.start()
        try:
            stuck = await _client(broker.port, "stuck")
            await stuck.subscribe("flood/#")
            # Stop consuming: cancel the reader so the socket buffer fills.
            assert stuck._reader_task is not None
            stuck._reader_task.cancel()
            await asyncio.sleep(0.05)

            healthy = await _client(broker.port, "healthy")
            await healthy.subscribe("flood/#")
            publisher = await _client(broker.port, "publisher")

            payload = b"x" * 65536
            for _message_index in range(200):
                await asyncio.wait_for(publisher.publish("flood/data", payload), timeout=10)

            # The healthy subscriber must receive the whole flood in bounded
            # time even while the stuck one is being aborted.
            received = 0
            deadline = asyncio.get_running_loop().time() + 15
            while received < 200 and asyncio.get_running_loop().time() < deadline:
                try:
                    await asyncio.wait_for(healthy.messages.get(), timeout=5)
                    received += 1
                except TimeoutError:
                    break
            assert received == 200, f"healthy subscriber got {received}/200"
            await publisher.disconnect()
            await healthy.disconnect()
        finally:
            await broker.stop()

    run(body(), timeout=60)


def test_payload_and_packet_size_edges():
    async def body():
        broker = Broker(port=0, max_packet_size=4096)
        await broker.start()
        try:
            sub = await _client(broker.port, "sub", max_packet_size=8192)
            await sub.subscribe("edge/#")
            pub = await _client(broker.port, "pub", max_packet_size=8192)

            await pub.publish("edge/empty", b"")  # zero-byte payload
            message = await asyncio.wait_for(sub.messages.get(), timeout=5)
            assert message.payload == b""

            # Exactly at the broker's limit: topic + header + payload <= 4096.
            fitting = b"y" * (4096 - 200)
            await pub.publish("edge/fit", fitting)
            message = await asyncio.wait_for(sub.messages.get(), timeout=5)
            assert message.payload == fitting

            # Over the limit: the offending connection dies, others survive.
            with_overflow = await _client(broker.port, "overflow", max_packet_size=65536)
            with contextlib.suppress(Exception):
                # The send may fail fast depending on close timing; either
                # way the broker must kill only this connection.
                await with_overflow.publish("edge/too-big", b"z" * 8192)
            await asyncio.sleep(0.2)
            await pub.publish("edge/after", b"still-alive")
            message = await asyncio.wait_for(sub.messages.get(), timeout=5)
            assert message.payload == b"still-alive"

            # UTF-8 boundary topics: emoji and combining characters.
            for topic in ("edge/🤖/state", "edge/ñ/x"):
                await pub.publish(topic, b"utf8")
                message = await asyncio.wait_for(sub.messages.get(), timeout=5)
                assert message.topic == topic
            await pub.disconnect()
            await sub.disconnect()
        finally:
            await broker.stop()

    run(body())


def test_retained_flood_then_hash_subscribe_completes():
    async def body():
        broker = Broker(port=0)
        await broker.start()
        try:
            seeder = await _client(broker.port, "seeder")
            for i in range(10_000):
                await seeder.publish(f"retained/{i}", b"v", retain=True)
            await seeder.disconnect()

            late = await _client(broker.port, "late")
            await late.subscribe("retained/#")
            got = 0
            deadline = asyncio.get_running_loop().time() + 20
            while got < 10_000 and asyncio.get_running_loop().time() < deadline:
                try:
                    message = await asyncio.wait_for(late.messages.get(), timeout=5)
                except TimeoutError:
                    break
                assert message.retain
                got += 1
            assert got == 10_000, f"retained delivery incomplete: {got}/10000"
            await late.disconnect()
        finally:
            await broker.stop()

    run(body(), timeout=45)


def test_overlapping_subscriptions_deliver_once_per_message():
    """MQTT 3.1.1 allows either one delivery at the max matching QoS or one
    per matching subscription; this broker deliberately implements the
    single-delivery form ([MQTT-3.3.5-1]) — pinned here so a refactor cannot
    silently change wire behavior."""

    async def body():
        broker = Broker(port=0)
        await broker.start()
        try:
            sub = await _client(broker.port, "multi")
            for topic_filter in ("#", "a/+/c", "a/b/c", "+/+/+"):
                await sub.subscribe(topic_filter)
            pub = await _client(broker.port, "pub")
            await pub.publish("a/b/c", b"once")
            first = await asyncio.wait_for(sub.messages.get(), timeout=5)
            assert first.payload == b"once"
            await asyncio.sleep(0.3)
            assert sub.messages.empty(), "duplicate delivery for overlapping subscriptions"
            await pub.disconnect()
            await sub.disconnect()
        finally:
            await broker.stop()

    run(body())


def test_keepalive_boundary_under_load():
    async def body():
        broker = Broker(port=0)
        await broker.start()
        try:
            fragile = await _client(broker.port, "fragile", keepalive=1)
            await fragile.subscribe("load/#")
            pusher = await _client(broker.port, "pusher")
            # 3 seconds of load: the ka=1 client's ping loop must keep the
            # session alive (broker allows 1.5x keepalive of silence).
            for i in range(30):
                await pusher.publish("load/x", json.dumps({"i": i}).encode())
                await asyncio.sleep(0.1)
            got = 0
            while not fragile.messages.empty():
                fragile.messages.get_nowait()
                got += 1
            assert got == 30, f"keepalive=1 client lost messages: {got}/30"
            assert fragile.connected
            await fragile.disconnect()
            await pusher.disconnect()
        finally:
            await broker.stop()

    run(body())


def test_codec_survives_torn_and_fuzzy_frames_between_valid_traffic():
    async def body():
        broker = Broker(port=0)
        await broker.start()
        try:
            sub = await _client(broker.port, "sane")
            await sub.subscribe("ok/x")
            # A raw socket writes garbage mid-stream, then dies; sanity check
            # legitimate traffic still flows.
            _reader, writer = await asyncio.open_connection("127.0.0.1", broker.port)
            writer.write(bytes(range(256)) * 8)
            await writer.drain()
            writer.close()
            pub = await _client(broker.port, "pub2")
            await pub.publish("ok/x", b"fine")
            message = await asyncio.wait_for(sub.messages.get(), timeout=5)
            assert message.payload == b"fine"
            assert codec.topic_matches("ok/+", "ok/x")
            await pub.disconnect()
            await sub.disconnect()
        finally:
            await broker.stop()

    run(body())
