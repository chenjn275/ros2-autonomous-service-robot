# Hardware Setup

This robot profile targets:

- Intel RealSense D425i depth camera
- AgileX Scout Mini base
- Livox MID360 LiDAR
- Intel NUC Ultra onboard computer
- AgileX Piper standard arm

Vendor drivers are not vendored into this repository. Fetch them into the ignored external workspace:

```bash
bash scripts/fetch_hardware_drivers.sh
```

If the Piper ROS2 branch is required, specify it explicitly:

```bash
PIPER_BRANCH=<ros2-branch-name> bash scripts/fetch_hardware_drivers.sh
```

## CAN

Scout Mini normally uses `can0`; Piper uses `can1` in this repository profile.

```bash
sudo ip link set can0 down || true
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

sudo ip link set can1 down || true
sudo ip link set can1 type can bitrate 1000000
sudo ip link set can1 up
```

## Network

MID360 requires the NUC network interface and the LiDAR to be on the same static subnet. Edit:

```text
ros2_ws/src/service_robot_hardware/config/mid360.yaml
```

## Launch

Hardware bringup wrapper:

```bash
ros2 launch service_robot_hardware hardware_bringup.launch.py
```

Individual wrappers:

```bash
ros2 launch service_robot_hardware realsense_d425i.launch.py
ros2 launch service_robot_hardware scout_mini_base.launch.py
ros2 launch service_robot_hardware mid360.launch.py
ros2 launch service_robot_hardware piper_arm.launch.py
```

The wrappers are conditional. If a vendor driver is not installed in the sourced workspace, launch prints a clear message instead of crashing the whole robot bringup.
