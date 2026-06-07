# Capability Matrix

## Core ROS2

- Workspace organization with `service_robot_*` packages
- Topic communication for sensors, perception, task flow, and system health
- Service communication via `/system/health_check`
- Action communication via optional Nav2 `NavigateToPose`
- Python nodes for perception, tasks, and description helpers
- C++ nodes for system monitoring

## Robot Model And Simulation

- URDF/xacro service robot model
- D425i, MID360, Piper, and NUC mount frames
- Gazebo Classic indoor world
- RViz robot model visualization

## Navigation And Localization

- Navigation2 DWB/NavFn configuration
- AMCL and map_server launch
- SLAM Toolbox launch
- TEB parameter template
- Point-LIO/Fast-LIO parameter templates

## Perception

- OpenCV QR detection
- YOLO no-model mode and configurable model path
- Annotated image publishing

## Hardware Interfaces

- Intel RealSense D425i wrapper launch
- AgileX Scout Mini CAN base wrapper launch
- Livox MID360 wrapper launch
- AgileX Piper standard arm wrapper launch
- NUC Ultra onboard computer profile

## Engineering

- Build/install/check scripts
- Dockerfile
- GitHub Actions build check
- rosbag recording script
- Demo assets and verification report
