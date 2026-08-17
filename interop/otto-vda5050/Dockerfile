# OTTO Motors / InOrbit / Ekumen open-source VDA 5050 <-> ROS 2 connector,
# built at a pinned commit, plus this repo's mock adapter standing in for the
# robot's navigation stack. The connector's mqtt_bridge + controller are run
# UNMODIFIED — they are the external implementation our master control and
# broker are being validated against.
#
# Upstream: https://github.com/inorbit-ai/ros_amr_interop (humble-devel)
FROM ros:humble-ros-base

ARG CONNECTOR_REPO=https://github.com/inorbit-ai/ros_amr_interop.git
# humble-devel @ 2026-07-28
ARG CONNECTOR_COMMIT=9536d90ad35a22bd950e1d5d7e300a0df6fc0ed6

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    git \
    python3-colcon-common-extensions \
    python3-paho-mqtt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /dev_ws

RUN git clone ${CONNECTOR_REPO} /tmp/ros_amr_interop \
    && git -C /tmp/ros_amr_interop checkout ${CONNECTOR_COMMIT} \
    && mkdir -p src \
    && mv /tmp/ros_amr_interop/vda5050_connector src/vda5050_connector \
    && mv /tmp/ros_amr_interop/vda5050_msgs src/vda5050_msgs \
    && mv /tmp/ros_amr_interop/vda5050_serializer src/vda5050_serializer \
    && rm -rf /tmp/ros_amr_interop

COPY mock_adapter src/vda5050_mock_adapter

# BUILD_TESTING=OFF: the connector's test target needs ament lint packages
# absent from ros-base; we run the connector, not its lint suite.
RUN /bin/bash -c "source /opt/ros/humble/setup.bash \
    && colcon build --cmake-args -DBUILD_TESTING=OFF"

COPY config/connector_interop.yaml /dev_ws/connector_interop.yaml
COPY entrypoint.sh /dev_ws/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/dev_ws/entrypoint.sh"]
