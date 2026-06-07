# Hardware Driver Sources

This package keeps hardware-specific launch wrappers and configuration templates in this repository while leaving vendor drivers outside the repository.

Official or upstream sources used by the wrappers:

- Intel RealSense ROS wrapper: `https://github.com/IntelRealSense/realsense-ros`
- Livox ROS Driver 2: `https://github.com/Livox-SDK/livox_ros_driver2`
- AgileX Scout ROS2: `https://github.com/agilexrobotics/scout_ros2`
- AgileX Piper ROS: `https://github.com/agilexrobotics/piper_ros`

Drivers are fetched into `external_ws/src`, which is ignored by Git. The service robot repository remains a standalone project without vendor repository history.
