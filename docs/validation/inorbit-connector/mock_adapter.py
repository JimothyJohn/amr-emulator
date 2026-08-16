#!/usr/bin/env python3
"""Minimal VDA5050 adapter for the InOrbit/OTTO vda5050_connector.

Stands in for a real robot: navigation goals succeed after a short simulated
drive, VDA actions finish immediately, and GetState reports a healthy AGV.
This lets the connector's mqtt_bridge + controller run their full VDA5050
protocol logic without Gazebo/nav2.
"""

import math
import time

import rclpy
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from vda5050_connector.action import NavigateThroughNodes, NavigateToNode, ProcessVDAAction
from vda5050_connector.srv import GetState, SupportedActions
from vda5050_msgs.msg import AGVPosition, BatteryState, CurrentAction, SafetyState, Velocity

NAMESPACE = "/vda5050/robots/robot_1"


class MockAdapter(Node):
    def __init__(self) -> None:
        super().__init__("adapter", namespace=NAMESPACE)
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.create_service(GetState, "adapter/get_state", self.get_state)
        self.create_service(SupportedActions, "adapter/supported_actions", self.supported)
        ActionServer(self, ProcessVDAAction, "adapter/vda_action", self.process_action)
        ActionServer(self, NavigateToNode, "adapter/nav_to_node", self.nav_to_node)
        ActionServer(
            self, NavigateThroughNodes, "adapter/nav_through_nodes", self.nav_through_nodes
        )
        self.get_logger().info("mock adapter ready")

    def get_state(self, _request, response):
        response.state.driving = False
        response.state.operating_mode = "AUTOMATIC"
        response.state.agv_position = self._position()
        response.state.battery_state = BatteryState(battery_charge=95.0, charging=False)
        response.state.safety_state = SafetyState(e_stop="NONE", field_violation=False)
        return response

    def supported(self, _request, response):
        return response

    def _position(self) -> AGVPosition:
        return AGVPosition(
            position_initialized=True,
            localization_score=1.0,
            x=self.x,
            y=self.y,
            theta=self.theta,
        )

    def process_action(self, goal_handle):
        action = goal_handle.request.action
        self.get_logger().info(f"executing VDA action {action.action_type}")
        result = ProcessVDAAction.Result()
        result.result = CurrentAction(
            action_id=action.action_id,
            action_status=CurrentAction.FINISHED,
            result_description="mock adapter executed",
        )
        goal_handle.succeed()
        return result

    def _drive_to(self, node, goal_handle, feedback):
        if node.node_position:
            tx, ty = node.node_position.x, node.node_position.y
        else:
            tx, ty = self.x, self.y
        steps = 10
        for i in range(1, steps + 1):
            self.x += (tx - self.x) / (steps - i + 1)
            self.y += (ty - self.y) / (steps - i + 1)
            self.theta = math.atan2(ty - self.y, tx - self.x) if i < steps else self.theta
            feedback.position = self._position()
            feedback.velocity = Velocity(vx=0.5, vy=0.0, omega=0.0)
            goal_handle.publish_feedback(feedback)
            time.sleep(0.1)
        self.x, self.y = tx, ty

    def nav_to_node(self, goal_handle):
        node = goal_handle.request.node
        self.get_logger().info(f"navigating to node {node.node_id}")
        self._drive_to(node, goal_handle, NavigateToNode.Feedback())
        goal_handle.succeed()
        return NavigateToNode.Result()

    def nav_through_nodes(self, goal_handle):
        feedback = NavigateThroughNodes.Feedback()
        for node in goal_handle.request.nodes:
            self.get_logger().info(f"navigating through node {node.node_id}")
            self._drive_to(node, goal_handle, feedback)
            feedback.last_node = node
            goal_handle.publish_feedback(feedback)
        goal_handle.succeed()
        return NavigateThroughNodes.Result()


def main() -> None:
    rclpy.init()
    node = MockAdapter()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
