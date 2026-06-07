FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    can-utils \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-yaml \
    v4l-utils \
    ros-humble-ament-cmake \
    ros-humble-rclcpp \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-rviz2 \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-moveit \
    ros-humble-moveit-resources-panda-description \
    ros-humble-moveit-resources-panda-moveit-config \
    ros-humble-vision-msgs \
    ros-humble-std-srvs \
    ros-humble-rosbag2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/ros2-autonomous-service-robot
COPY . .

RUN source /opt/ros/humble/setup.bash && \
    cd ros2_ws && \
    colcon build --symlink-install

CMD ["/bin/bash"]
