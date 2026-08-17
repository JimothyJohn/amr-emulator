#!/bin/bash
# Launch the unmodified vda5050_connector (mqtt_bridge + controller) and the
# mock adapter inside one container. MQTT_HOST/MQTT_PORT point at the broker
# on the Docker host (the interop driver's embedded broker).
# No -u: ROS setup.bash reads unbound variables.
set -e
export PYTHONUNBUFFERED=1

source /opt/ros/humble/setup.bash
source /dev_ws/install/setup.bash

MQTT_HOST="${MQTT_HOST:-host.docker.internal}"
MQTT_PORT="${MQTT_PORT:-1883}"

sed -e "s/@MQTT_HOST@/${MQTT_HOST}/" -e "s/@MQTT_PORT@/${MQTT_PORT}/" \
    /dev_ws/connector_interop.yaml > /tmp/params.yaml

ros2 run vda5050_mock_adapter mock_adapter \
    --ros-args -r __ns:=/vda5050 --params-file /tmp/params.yaml &
ros2 run vda5050_connector vda5050_controller.py \
    --ros-args -r __ns:=/vda5050 -r __node:=controller --params-file /tmp/params.yaml &
ros2 run vda5050_connector mqtt_bridge.py \
    --ros-args -r __ns:=/vda5050 -r __node:=mqtt_bridge --params-file /tmp/params.yaml &

# Exit the container if any node dies so failures surface in the driver.
wait -n
