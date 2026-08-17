"""Pure compilation tests: missions -> spec-correct orders and updates.

These assert the structural contract the acceptance process (Figure 8)
enforces, and additionally push every compiled message through the official
schema validator — the same oracle the wire path uses.
"""

import pytest
from vda5050_emulator.validation import validation_errors
from vda5050_master import Mission, Waypoint, action


def _mission(n: int = 4) -> Mission:
    return Mission([Waypoint(x=float(i), y=0.0) for i in range(n)], name="m")


def _validated(body: dict, version: str) -> dict:
    envelope = {
        "headerId": 0,
        "timestamp": "2026-01-01T00:00:00.00Z",
        "version": version,
        "manufacturer": "t",
        "serialNumber": "t-1",
        **body,
    }
    assert validation_errors("order", envelope, tag=version) == []
    return body


def test_order_structure_and_full_release():
    order = _validated(_mission(4).order(version="3.0.0", order_id="o-1"), "3.0.0")
    assert order["orderUpdateId"] == 0
    assert [n["sequenceId"] for n in order["nodes"]] == [0, 2, 4, 6]
    assert [e["sequenceId"] for e in order["edges"]] == [1, 3, 5]
    assert all(n["released"] for n in order["nodes"])
    assert all(e["released"] for e in order["edges"])


def test_base_horizon_split_keeps_released_prefix_contiguous():
    order = _mission(4).order(version="3.0.0", order_id="o-1", release=2)
    assert [n["released"] for n in order["nodes"]] == [True, True, False, False]
    # An edge is released only when both adjacent nodes are: 2 nodes -> 1 edge.
    assert [e["released"] for e in order["edges"]] == [True, False, False]


def test_v2_edges_carry_node_ids_and_v3_edges_do_not():
    v2 = _validated(_mission(2).order(version="2.0.0", order_id="o"), "2.0.0")
    assert v2["edges"][0]["startNodeId"] == v2["nodes"][0]["nodeId"]
    assert v2["edges"][0]["endNodeId"] == v2["nodes"][1]["nodeId"]
    v3 = _validated(_mission(2).order(version="3.0.0", order_id="o"), "3.0.0")
    assert "startNodeId" not in v3["edges"][0]


def test_update_stitches_at_the_decision_point():
    mission = _mission(5)
    order = mission.order(version="3.0.0", order_id="o", release=2)
    update = _validated(
        mission.update(
            version="3.0.0",
            order_id="o",
            order_update_id=1,
            previous_release=2,
            release=4,
        ),
        "3.0.0",
    )
    # First node of the update is the last released node, sequenceId intact.
    assert update["nodes"][0]["nodeId"] == order["nodes"][1]["nodeId"]
    assert update["nodes"][0]["sequenceId"] == order["nodes"][1]["sequenceId"] == 2
    assert update["orderUpdateId"] == 1
    # Everything from the stitch onward is re-sent; release grows to 4.
    assert [n["sequenceId"] for n in update["nodes"]] == [2, 4, 6, 8]
    assert [n["released"] for n in update["nodes"]] == [True, True, True, False]
    assert [e["released"] for e in update["edges"]] == [True, True, False]


def test_update_full_release_releases_trailing_edge():
    update = _mission(3).update(
        version="3.0.0", order_id="o", order_update_id=1, previous_release=1, release=3
    )
    assert all(n["released"] for n in update["nodes"])
    assert all(e["released"] for e in update["edges"])


def test_actions_get_ids_and_are_carried_on_nodes():
    pick = action("pick", blocking_type="HARD", parameters={"stationType": "shelf"})
    mission = Mission([Waypoint(x=0, y=0), Waypoint(x=1, y=0, actions=(pick,))], name="m")
    assert len(mission.action_ids) == 1
    order = mission.order(version="3.0.0", order_id="o")
    assert order["nodes"][1]["actions"][0]["actionId"] == mission.action_ids[0]


def test_compile_rejects_out_of_range_arguments():
    mission = _mission(3)
    with pytest.raises(ValueError):
        mission.order(version="3.0.0", order_id="o", release=0)
    with pytest.raises(ValueError):
        mission.order(version="3.0.0", order_id="o", release=4)
    with pytest.raises(ValueError):
        mission.update(
            version="3.0.0", order_id="o", order_update_id=0, previous_release=1, release=2
        )
    with pytest.raises(ValueError):
        # The base never shrinks.
        mission.update(
            version="3.0.0", order_id="o", order_update_id=1, previous_release=2, release=1
        )
    with pytest.raises(ValueError):
        Mission([])


def test_deviation_shape_differs_by_version_family():
    waypoints = [Waypoint(x=0, y=0, deviation=0.7)]
    v2 = Mission(waypoints, name="m").order(version="2.0.0", order_id="o")
    assert v2["nodes"][0]["nodePosition"]["allowedDeviationXY"] == 0.7
    v3 = Mission(waypoints, name="m").order(version="3.0.0", order_id="o")
    assert v3["nodes"][0]["nodePosition"]["allowedDeviationXY"] == {
        "a": 0.7,
        "b": 0.7,
        "theta": 0.0,
    }
