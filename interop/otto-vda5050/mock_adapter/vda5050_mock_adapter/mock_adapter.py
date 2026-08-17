#!/usr/bin/env python3
"""Instantly-succeeding adapter for the vda5050_connector.

Serves the four interfaces the connector's controller requires from an
adapter (GetState, SupportedActions, NavigateToNode, ProcessVDAAction) with
a robot that teleports: navigation goals succeed after a short delay and
the reported pose jumps to the target node. This keeps the connector's
controller and mqtt_bridge — the code under interop test — running
unmodified, without Gazebo or Nav2.

Modeled on the TB3 adapter from inorbit-ai/vda5050_adapter_examples.
"""

import time

import rclpy
from rclpy.action import ActionServer
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from vda5050_connector.action import NavigateToNode, ProcessVDAAction
from vda5050_connector.srv import GetState, SupportedActions
from vda5050_msgs.msg import (
    AGVPosition,
    BatteryState,
    CurrentAction,
    OrderState,
    SafetyState,
    Velocity,
)

NODE_NAME = "mock_adapter"
NAV_SECONDS = 0.5


class MockAdapter(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.declare_parameter("robot_name", "robot_1")
        self.declare_parameter("manufacturer_name", "robots")

        robot_name = self.get_parameter("robot_name").value
        manufacturer = self.get_parameter("manufacturer_name").value
        base = f"{self.get_namespace()}/{manufacturer}/{robot_name}/"

        self._position = AGVPosition(
            position_initialized=True,
            localization_score=1.0,
            map_id="map",
        )
        self._velocity = Velocity()
        self._driving = False

        self.create_service(GetState, base + "adapter/get_state", self.get_state_cb)
        self.create_service(
            SupportedActions,
            base + "adapter/supported_actions",
            self.supported_actions_cb,
        )
        ActionServer(
            node=self,
            action_type=NavigateToNode,
            action_name=base + "adapter/nav_to_node",
            execute_callback=self.nav_to_node_cb,
            callback_group=MutuallyExclusiveCallbackGroup(),
        )
        ActionServer(
            node=self,
            action_type=ProcessVDAAction,
            action_name=base + "adapter/vda_action",
            execute_callback=self.process_vda_action_cb,
            callback_group=MutuallyExclusiveCallbackGroup(),
        )
        self.get_logger().info(f"{NODE_NAME} serving under {base}")

    def get_state_cb(self, request, response):
        state = OrderState()
        state.agv_position = self._position
        state.velocity = self._velocity
        state.driving = self._driving
        state.paused = False
        state.operating_mode = OrderState.AUTOMATIC
        state.battery_state = BatteryState(battery_charge=87.0, charging=False)
        state.safety_state = SafetyState(e_stop=SafetyState.NONE, field_violation=False)
        response.state = state
        return response

    def supported_actions_cb(self, request, response):
        return response

    def nav_to_node_cb(self, goal_handle):
        node = goal_handle.request.node
        self.get_logger().info(
            f"Navigating to node '{node.node_id}' ({node.node_position.x}, {node.node_position.y})"
        )
        self._driving = True
        time.sleep(NAV_SECONDS)
        self._position.x = node.node_position.x
        self._position.y = node.node_position.y
        self._position.theta = node.node_position.theta
        self._driving = False
        goal_handle.succeed()
        return NavigateToNode.Result()

    def process_vda_action_cb(self, goal_handle):
        action = goal_handle.request.action
        self.get_logger().info(f"Executing action '{action.action_type}' ({action.action_id})")
        current = CurrentAction(
            action_id=action.action_id,
            action_description=action.action_description,
            action_status=CurrentAction.RUNNING,
        )
        goal_handle.publish_feedback(ProcessVDAAction.Feedback(current_action=current))
        time.sleep(0.2)
        current.action_status = CurrentAction.FINISHED
        goal_handle.succeed()
        return ProcessVDAAction.Result(result=current)


def main(args=None):
    rclpy.init(args=args)
    node = MockAdapter()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
