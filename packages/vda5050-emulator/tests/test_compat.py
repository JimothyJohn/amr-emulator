"""Compatibility behaviors proven necessary by external master controls.

NVIDIA Isaac Mission Dispatch (validated live against the emulator) publishes
instant actions in the VDA 5050 1.x message shape — the array is called
``instantActions`` — while stamping ``version: 2.0.0``, and it redelivers the
same instant action every ~100 ms until the robot reports a terminal status.
The emulator executes such actions anyway (while still reporting the schema
deviation as a validationError WARNING) and treats redelivery of an already
known actionId as idempotent.
"""

from __future__ import annotations

from conftest import Stack, await_error, run


def _legacy_instant_actions(stack: Stack, action_id: str) -> dict:
    return {
        "headerId": 797,
        "timestamp": "2026-01-01T00:00:00.000000",
        "version": "2.0.0",
        "manufacturer": "",
        "serialNumber": "",
        "instantActions": [
            {
                "actionType": "factsheetRequest",
                "actionId": action_id,
                "blockingType": "HARD",
                "actionParameters": [],
                "actionDescription": "",
            }
        ],
    }


def test_legacy_instant_actions_field_is_executed_and_flagged():
    async def body():
        async with Stack("2.1.0") as stack:
            factsheets_before = len(stack.published["factsheet"])
            await stack.m.publish_raw(
                "instantActions", _legacy_instant_actions(stack, "instantaction-n0")
            )
            entry = await stack.m.action_status(
                "instantaction-n0", statuses=("FINISHED",), timeout=10
            )
            assert entry["actionStatus"] == "FINISHED"
            # The deviation is still reported, not silently accepted.
            error = await await_error(stack, "validationError")
            assert "actions" in error["errorDescription"]
            # The factsheet actually went out again in response.
            state = await stack.m.next_state(timeout=5)
            assert state is not None
            for _ in range(100):
                if len(stack.published["factsheet"]) > factsheets_before:
                    break
                await __import__("asyncio").sleep(0.02)
            assert len(stack.published["factsheet"]) > factsheets_before

    run(body())


def test_instant_action_redelivery_is_idempotent():
    async def body():
        async with Stack("2.1.0") as stack:
            for _ in range(25):  # Mission Dispatch redelivers until confirmed
                await stack.m.publish_raw(
                    "instantActions", _legacy_instant_actions(stack, "instantaction-n0")
                )
            await stack.m.action_status("instantaction-n0", statuses=("FINISHED",), timeout=10)
            state = await stack.m.next_state(timeout=5)
            matching = [a for a in state["actionStates"] if a["actionId"] == "instantaction-n0"]
            assert len(matching) == 1, "redelivery must not duplicate action states"

    run(body())


def test_legacy_field_works_on_2_0_0_despite_vacuous_schema():
    # The 2.0.0 instantActions schema has no required fields, so a 1.x-shaped
    # message raises no schema problems — the compat path must key off the
    # missing `actions` field, not the schema verdict (found live against
    # Isaac Mission Dispatch driving the MiR adapter).
    async def body():
        async with Stack("2.0.0") as stack:
            await stack.m.publish_raw(
                "instantActions", _legacy_instant_actions(stack, "instantaction-n0")
            )
            entry = await stack.m.action_status(
                "instantaction-n0", statuses=("FINISHED", "FAILED"), timeout=10
            )
            assert entry["actionStatus"] in ("FINISHED", "FAILED")

    run(body())


def test_spec_shaped_actions_field_still_works_untouched():
    async def body():
        async with Stack("2.1.0") as stack:
            aid = await stack.m.send_instant_action("stateRequest")
            await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)
            state = await stack.m.next_state(timeout=5)
            assert not any(e["errorType"] == "validationError" for e in state["errors"])

    run(body())
