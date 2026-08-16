#!/bin/bash
# Build and launch the InOrbit vda5050_connector with the mock adapter,
# pointed at the vda5050-emulator's broker on the docker host (port 1884).
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null
apt-get install -qq -y python3-paho-mqtt ros-humble-pluginlib >/dev/null 2>&1 || \
  apt-get install -qq -y python3-pip ros-humble-pluginlib >/dev/null && pip3 -q install paho-mqtt 2>/dev/null || true
source /opt/ros/humble/setup.bash
cd /dev_ws
colcon build --symlink-install --packages-select vda5050_msgs vda5050_serializer vda5050_connector \
  --cmake-args -DBUILD_TESTING=OFF 2>&1 | tail -3
source install/setup.bash
python3 /dev_ws/src/mock_adapter.py &
sleep 2
ros2 launch vda5050_connector mqtt_bridge.launch.py parameters_config_file:=/dev_ws/src/params.yaml &
sleep 2
ros2 launch vda5050_connector controller.launch.py parameters_config_file:=/dev_ws/src/params.yaml &
wait
