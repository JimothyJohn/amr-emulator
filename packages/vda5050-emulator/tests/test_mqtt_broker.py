"""End-to-end behavior of the embedded broker over real TCP on ephemeral ports."""

import asyncio
import contextlib

import pytest
from vda5050_emulator.mqtt import Broker, Message, MQTTClient, MQTTError, codec

RECV_TIMEOUT = 5.0


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, timeout=30))


@contextlib.asynccontextmanager
async def broker(**kwargs):
    b = Broker(**kwargs)
    await b.start()
    try:
        yield b
    finally:
        await b.stop()


@contextlib.asynccontextmanager
async def client(b: Broker, client_id: str, **kwargs):
    c = MQTTClient(client_id, "127.0.0.1", b.port, **kwargs)
    await c.connect()
    try:
        yield c
    finally:
        if c.connected:
            await c.disconnect()


async def recv(c: MQTTClient) -> Message:
    return await asyncio.wait_for(c.messages.get(), timeout=RECV_TIMEOUT)


async def assert_no_message(c: MQTTClient, wait: float = 0.2) -> None:
    with pytest.raises(TimeoutError):
        await asyncio.wait_for(c.messages.get(), timeout=wait)


def test_publish_subscribe_round_trip():
    async def main():
        async with broker() as b, client(b, "sub") as sub, client(b, "pub") as pub:
            await sub.subscribe("uagv/v3/+/+/state")
            await pub.publish("uagv/v3/kit/0001/state", b'{"x":1}')
            message = await recv(sub)
            assert message.topic == "uagv/v3/kit/0001/state"
            assert message.payload == b'{"x":1}'
            assert message.qos == 0

    run(main())


def test_qos1_publish_and_delivery_qos_is_min():
    async def main():
        async with broker() as b, client(b, "sub") as sub, client(b, "pub") as pub:
            await sub.subscribe("q1", qos=1)
            await sub.subscribe("q0", qos=0)
            await pub.publish("q1", b"a", qos=1)  # waits for PUBACK
            assert (await recv(sub)).qos == 1
            await pub.publish("q0", b"b", qos=1)
            assert (await recv(sub)).qos == 0

    run(main())


def test_retained_message_delivered_on_late_subscribe_and_cleared():
    async def main():
        async with broker() as b:
            async with client(b, "pub") as pub:
                await pub.publish("cfg/x", b"v1", retain=True)
            async with client(b, "late") as late:
                await late.subscribe("cfg/#")
                message = await recv(late)
                assert (message.payload, message.retain) == (b"v1", True)
            async with client(b, "pub2") as pub2:
                await pub2.publish("cfg/x", b"", retain=True)  # clears
            async with client(b, "later") as later:
                await later.subscribe("cfg/#")
                await assert_no_message(later)

    run(main())


def test_wildcards_and_dollar_topics():
    async def main():
        async with broker() as b, client(b, "sub") as sub, client(b, "pub") as pub:
            await sub.subscribe("#")
            await pub.publish("$internal/x", b"hidden")
            await pub.publish("visible", b"seen")
            assert (await recv(sub)).topic == "visible"
            await sub.subscribe("$internal/#")
            await pub.publish("$internal/x", b"now-visible")
            assert (await recv(sub)).payload == b"now-visible"

    run(main())


def test_unsubscribe_stops_delivery():
    async def main():
        async with broker() as b, client(b, "sub") as sub, client(b, "pub") as pub:
            await sub.subscribe("t")
            await pub.publish("t", b"1")
            await recv(sub)
            await sub.unsubscribe("t")
            await pub.publish("t", b"2")
            await assert_no_message(sub)

    run(main())


def test_last_will_fires_on_drop_not_on_graceful_disconnect():
    async def main():
        async with broker() as b, client(b, "watcher") as watcher:
            await watcher.subscribe("conn/+")
            will = Message(topic="conn/a", payload=b"BROKEN", retain=False)
            agv = MQTTClient("agv-a", "127.0.0.1", b.port, will=will)
            await agv.connect()
            await agv.disconnect()  # graceful: no will
            await assert_no_message(watcher)
            agv2 = MQTTClient("agv-b", "127.0.0.1", b.port, will=Message("conn/b", b"BROKEN"))
            await agv2.connect()
            await agv2.drop()  # abrupt: will fires
            message = await recv(watcher)
            assert (message.topic, message.payload) == ("conn/b", b"BROKEN")

    run(main())


def test_disconnect_client_fires_will():
    async def main():
        async with broker() as b, client(b, "watcher") as watcher:
            await watcher.subscribe("conn/x")
            agv = MQTTClient("agv-x", "127.0.0.1", b.port, will=Message("conn/x", b"BROKEN"))
            await agv.connect()
            assert await b.disconnect_client("agv-x") is True
            assert (await recv(watcher)).payload == b"BROKEN"
            assert await b.disconnect_client("nobody") is False

    run(main())


def test_takeover_publishes_old_will():
    async def main():
        async with broker() as b, client(b, "watcher") as watcher:
            await watcher.subscribe("conn/dup")
            first = MQTTClient("dup", "127.0.0.1", b.port, will=Message("conn/dup", b"OLD"))
            await first.connect()
            second = MQTTClient("dup", "127.0.0.1", b.port)
            await second.connect()
            assert (await recv(watcher)).payload == b"OLD"
            await second.disconnect()

    run(main())


def test_retained_will():
    async def main():
        async with broker() as b:
            agv = MQTTClient(
                "agv", "127.0.0.1", b.port, will=Message("conn/agv", b"BROKEN", retain=True)
            )
            await agv.connect()
            await agv.drop()
            async with client(b, "late") as late:
                await late.subscribe("conn/agv")
                message = await recv(late)
                assert (message.payload, message.retain) == (b"BROKEN", True)

    run(main())


def test_auth_required_and_rejected():
    async def main():
        async with broker(username="fleet", password="s3cret") as b:
            good = MQTTClient("ok", "127.0.0.1", b.port, username="fleet", password="s3cret")
            await good.connect()
            await good.disconnect()
            bad = MQTTClient("nope", "127.0.0.1", b.port, username="fleet", password="wrong")
            with pytest.raises(MQTTError):
                await bad.connect()
            anon = MQTTClient("anon", "127.0.0.1", b.port)
            with pytest.raises(MQTTError):
                await anon.connect()

    run(main())


def test_keepalive_timeout_fires_will():
    async def main():
        async with broker() as b, client(b, "watcher") as watcher:
            await watcher.subscribe("conn/quiet")
            reader, writer = await asyncio.open_connection("127.0.0.1", b.port)
            writer.write(
                codec.encode(
                    codec.Connect(
                        client_id="quiet",
                        keepalive=1,
                        will_topic="conn/quiet",
                        will_payload=b"BROKEN",
                    )
                )
            )
            await writer.drain()
            connack = await codec.read_packet(reader.readexactly)
            assert isinstance(connack, codec.ConnAck)
            # Send nothing: the broker must sever within 1.5x keepalive and fire the will.
            message = await recv(watcher)
            assert message.payload == b"BROKEN"
            writer.close()

    run(main())


def test_garbage_bytes_close_only_that_connection():
    async def main():
        async with broker() as b, client(b, "sub") as sub, client(b, "pub") as pub:
            await sub.subscribe("t")
            _, garbage_writer = await asyncio.open_connection("127.0.0.1", b.port)
            garbage_writer.write(b"\xff\xff\xff\xff\xff\xff\xffnonsense")
            await garbage_writer.drain()
            await asyncio.sleep(0.1)
            await pub.publish("t", b"still-works")
            assert (await recv(sub)).payload == b"still-works"
            garbage_writer.close()

    run(main())


def test_oversized_packet_closes_connection():
    async def main():
        async with broker(max_packet_size=1024) as b, client(b, "sub") as sub:
            await sub.subscribe("big")
            pub = MQTTClient("pub", "127.0.0.1", b.port)
            await pub.connect()
            with contextlib.suppress(MQTTError):
                await pub.publish("big", b"x" * 4096)
            await assert_no_message(sub)
            deadline = asyncio.get_running_loop().time() + RECV_TIMEOUT
            while pub.connected and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(0.05)
            assert not pub.connected

    run(main())


def test_protocol_level_refused():
    async def main():
        async with broker() as b:
            reader, writer = await asyncio.open_connection("127.0.0.1", b.port)
            good = codec.encode(codec.Connect(client_id="x"))
            level_index = good.index(b"MQTT") + 4
            writer.write(good[:level_index] + bytes([3]) + good[level_index + 1 :])
            await writer.drain()
            connack = await codec.read_packet(reader.readexactly)
            assert isinstance(connack, codec.ConnAck)
            assert connack.return_code == codec.CONNACK_REFUSED_PROTOCOL
            writer.close()

    run(main())


def test_empty_client_id_gets_assigned():
    async def main():
        async with broker() as b:
            a = MQTTClient("", "127.0.0.1", b.port)
            b2 = MQTTClient("", "127.0.0.1", b.port)
            await a.connect()
            await b2.connect()  # distinct auto ids: no takeover, both stay connected
            await asyncio.sleep(0.1)
            assert a.connected and b2.connected
            await a.disconnect()
            await b2.disconnect()

    run(main())


def test_concurrent_publishers_no_loss_or_corruption():
    async def main():
        async with broker() as b, client(b, "sub") as sub:
            await sub.subscribe("load/#", qos=1)
            publishers = 20
            each = 25

            async def blast(i: int) -> None:
                async with client(b, f"pub-{i}") as pub:
                    for n in range(each):
                        await pub.publish(f"load/{i}", f"{i}:{n}".encode(), qos=1)

            await asyncio.gather(*(blast(i) for i in range(publishers)))
            seen: set[bytes] = set()
            for _ in range(publishers * each):
                seen.add((await recv(sub)).payload)
            assert len(seen) == publishers * each
            for i in range(publishers):
                for n in range(each):
                    assert f"{i}:{n}".encode() in seen

    run(main())
