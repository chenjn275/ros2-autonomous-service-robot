# ROS2 Autonomous Service Robot

这是一个面向室内服务机器人场景的 ROS2 Humble 机器人软件仓库，覆盖仿真、机器人描述、导航定位、视觉感知、任务流程、机械臂接入、系统健康监控和真实硬件接口。项目采用 `service_robot_*` 多包结构组织，目标是让仓库 clone 后可以按 README 构建并运行基础 demo，同时能接入 D425i 深度相机、Scout Mini 底盘、MID360 激光雷达、NUC Ultra 主机和 Piper 标准版机械臂。

仓库不提交模型权重、外部厂商驱动源码、实机数据集、build/install/log 目录或大体积 rosbag。硬件驱动通过 apt 或 `scripts/fetch_hardware_drivers.sh` 拉取到被 Git 忽略的 `external_ws/src`。

## 已验证功能

在 Ubuntu 22.04.5 + ROS2 Humble 虚拟机中已验证：

- 11 个 ROS2 包可通过 `colcon build --symlink-install` 构建，其中包含 Python 包和 C++/ament_cmake 包。
- `service_robot_description` 提供服务机器人 xacro/URDF，包含 `base_footprint`、`base_link`、`laser_link`、`camera_link`、`camera_optical_link`、`d425i_link`、`mid360_link`、`piper_base_link`、`nuc_ultra_link`、左右轮 link。
- `robot_description` 保持 ROS 标准参数名。
- RViz/display 非 GUI 核心链路可启动：`robot_state_publisher` + 零位 `/joint_states` 发布器。
- Gazebo Classic headless 可启动室内 world 并 spawn 机器人。
- Gazebo 插件发布/订阅关键话题：
  - `/scan`
  - `/odom`
  - `/camera/image_raw`
  - `/cmd_vel`
- SLAM Toolbox launch 可启动并加载 Ceres solver。
- Navigation2 launch 可加载 `map_server`、AMCL、planner、controller、behavior 和 BT navigator；默认验证链路为去掉 velocity smoother/waypoint follower 的轻量 Nav2 栈。
- `demo_map.yaml` 可被 Nav2 map_server 加载。
- QR 节点订阅 `/camera/image_raw`，发布 `/perception/qr/result` 和 `/perception/qr/annotated`。
- YOLO 节点支持 no-model 模式，订阅 `/camera/image_raw`，发布 `/perception/yolo/detections` 和 `/perception/yolo/annotated`。
- `service_robot_tasks` 提供 YAML 驱动的服务任务流程 demo，支持 mock navigation 和可选 Nav2 `NavigateToPose` action。
- `service_robot_system` 提供 C++ 系统健康监控节点，订阅 `/scan`、`/odom`、`/cmd_vel`，发布 `/system/health`，并提供 `/system/health_check` Trigger service。
- ROS2 Topic、Service、Action 均有源码入口：Topic 用于传感器/感知/状态，Service 用于系统健康检查，Action 用于 Nav2 `NavigateToPose`。
- `service_robot_bringup demo.launch.py` 提供一键 demo 入口，可组合 Gazebo、感知、任务和系统健康节点；Nav2 通过独立 launch 或验证脚本启动。
- `service_robot_lio` 提供 Point-LIO / Fast-LIO 可选接入入口和服务机器人参数模板。
- `service_robot_hardware` 提供 D425i、Scout Mini、MID360、NUC Ultra、Piper 标准版硬件接口 launch 和参数模板。
- `service_robot_navigation` 提供 TEB 局部规划器参数模板；默认已验证链路仍使用 DWB。
- MoveIt2 Panda `move_group` 无 GUI demo 已验证可启动，日志提示 `You can start planning now!`；真实服务机器人/Piper/UMI 抓取闭环仍需要专用 MoveIt config、控制器和硬件/仿真驱动。
- rosbag2 录制脚本已提供。
- Dockerfile 和 GitHub Actions 构建检查已提供。

详细验证记录见 [docs/verification_report.md](docs/verification_report.md)。

## 包结构

- `service_robot_bringup`：顶层 launch 入口。
- `service_robot_description`：机器人 xacro/URDF、RViz 配置、零位关节状态发布器。
- `service_robot_simulation`：Gazebo Classic world 和 spawn launch。
- `service_robot_localization`：SLAM Toolbox 参数和 launch。
- `service_robot_navigation`：Navigation2 参数、demo map 和 launch。
- `service_robot_perception`：QR 与 YOLO 图像感知节点。
- `service_robot_manipulation`：MoveIt2/Piper/UMI 机械臂接入入口，已验证 Panda `move_group` 无 GUI demo。
- `service_robot_tasks`：任务级流程协调器，组织识别、导航、分类、模拟分拣和返回流程。
- `service_robot_lio`：Point-LIO / Fast-LIO 可选参数和 launch 入口。
- `service_robot_system`：C++ 系统健康监控、Topic 订阅、状态发布和 Trigger service。
- `service_robot_hardware`：真实硬件接口、外参、CAN/网络配置和条件 launch。

## 环境依赖

推荐环境：

- Ubuntu 22.04
- ROS2 Humble
- Python 3.10
- colcon
- Gazebo Classic / RViz2
- Navigation2
- SLAM Toolbox
- cv_bridge / image_transport
- rosbag2
- can-utils / v4l-utils

安装：

```bash
bash scripts/install_deps.sh
```

如果脚本无法使用 sudo，请手动安装：

```bash
sudo apt update
sudo apt install -y \
  can-utils python3-colcon-common-extensions python3-rosdep \
  v4l-utils \
  ros-humble-ament-cmake ros-humble-rclcpp \
  ros-humble-xacro ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2 ros-humble-gazebo-ros-pkgs \
  ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-slam-toolbox ros-humble-cv-bridge \
  ros-humble-moveit \
  ros-humble-moveit-resources-panda-description \
  ros-humble-moveit-resources-panda-moveit-config \
  ros-humble-image-transport ros-humble-vision-msgs \
  ros-humble-std-srvs ros-humble-rosbag2 \
  ros-humble-realsense2-camera python3-yaml
```

YOLO 有模型推理时额外安装：

```bash
pip3 install ultralytics
```

## 构建

```bash
bash scripts/build.sh
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 pkg list | grep service_robot
```

期望看到：

```text
service_robot_bringup
service_robot_description
service_robot_localization
service_robot_manipulation
service_robot_navigation
service_robot_perception
service_robot_simulation
service_robot_tasks
service_robot_lio
service_robot_system
service_robot_hardware
```

## 静态检查

```bash
bash scripts/check_python.sh
python3 -m py_compile ros2_ws/src/service_robot_perception/scripts/*.py
xacro ros2_ws/src/service_robot_description/urdf/service_robot.urdf.xacro > /tmp/service_robot.urdf
check_urdf /tmp/service_robot.urdf
```

## 运行 RViz / Robot Description Demo

无 GUI 验证：

```bash
ros2 launch service_robot_bringup display.launch.py use_rviz:=false
```

有 GUI：

```bash
ros2 launch service_robot_bringup display.launch.py
```

默认 `use_gui:=false`，使用本项目的零位关节状态发布器。需要 `joint_state_publisher_gui` 时：

```bash
ros2 launch service_robot_bringup display.launch.py use_gui:=true
```

## 运行 Gazebo Demo

Headless：

```bash
ros2 launch service_robot_simulation gazebo.launch.py gui:=false
```

检查话题：

```bash
ros2 topic list
ros2 topic info /scan
ros2 topic info /odom
ros2 topic info /camera/image_raw
ros2 topic info /cmd_vel
```

有 GUI：

```bash
ros2 launch service_robot_simulation gazebo.launch.py gui:=true
```

## 运行一键 Demo

默认启动 Gazebo headless、QR、YOLO no-model、任务流程和 C++ 系统健康节点：

```bash
ros2 launch service_robot_bringup demo.launch.py
```

Nav2 任务验证使用独立脚本：

```bash
bash scripts/run_nav_task_demo.sh
```

常用参数：

- `gui`：是否打开 Gazebo GUI，默认 `false`
- `start_perception`：是否启动 QR/YOLO，默认 `true`
- `start_tasks`：是否启动任务流程，默认 `true`
- `start_system`：是否启动 C++ 健康节点，默认 `true`

## 运行 SLAM

```bash
ros2 launch service_robot_localization slam.launch.py
```

需要同时有 `/scan`、`/odom` 和 `/tf`。建议与 Gazebo demo 同时运行。

## 运行 Navigation2

```bash
ros2 launch service_robot_navigation navigation.launch.py
```

单独启动 Nav2 时会等待 `odom -> base_footprint` TF，这是因为没有同时启动 Gazebo 或真实底盘。完整验证应先启动 Gazebo：

```bash
ros2 launch service_robot_simulation gazebo.launch.py gui:=false
ros2 launch service_robot_navigation navigation.launch.py
```

当前 Nav2 使用 DWB 局部规划器和 NavFn 全局规划器，已验证 Humble 插件加载。TEB 参数模板已提供，但未作为默认 controller 完成闭环验证。

## 运行二维码识别

```bash
ros2 launch service_robot_perception qr_detection.launch.py
```

接口：

- 订阅：`/camera/image_raw`
- 发布：`/perception/qr/result`
- 发布：`/perception/qr/annotated`

## 运行 YOLO 节点

默认 no-model 模式：

```bash
ros2 launch service_robot_perception yolo_detection.launch.py
```

no-model 模式下，节点不加载权重，只发布空 detections，并转发 annotated 图像。

配置模型：

```bash
ros2 launch service_robot_perception yolo_detection.launch.py model_path:=/path/to/model.pt confidence:=0.25
```

本仓库不提交 `.pt`、`.onnx`、`.engine` 等模型权重。轻量模型下载和配置方式见 [docs/yolo_model.md](docs/yolo_model.md)。

## rosbag 录制

```bash
bash scripts/record_demo_bag.sh
```

输出目录为 `bags/`，默认不提交到 Git。

## 运行 C++ 系统健康节点

```bash
ros2 launch service_robot_system system_health.launch.py
```

接口：

- 订阅：`/scan`
- 订阅：`/odom`
- 订阅：`/cmd_vel`
- 发布：`/system/health`
- 服务：`/system/health_check`

调用服务：

```bash
ros2 service call /system/health_check std_srvs/srv/Trigger {}
```

## 运行任务流程 Demo

默认 mock navigation，不要求 Nav2 已启动：

```bash
ros2 launch service_robot_tasks task_commander.launch.py
```

接口：

- 订阅：`/perception/qr/result`
- 订阅：`/perception/yolo/detections`
- 发布：`/tasks/status`

如果 Gazebo + Nav2 已经运行，可以让任务节点通过 Nav2 action 发送目标：

```bash
ros2 launch service_robot_tasks task_commander.launch.py use_nav:=true use_sim_time:=true
```

## 运行真实硬件接口

硬件配置文件位于：

```text
ros2_ws/src/service_robot_hardware/config/
```

拉取外部厂商驱动：

```bash
bash scripts/fetch_hardware_drivers.sh
```

启动硬件总入口：

```bash
ros2 launch service_robot_hardware hardware_bringup.launch.py
```

单独启动：

```bash
ros2 launch service_robot_hardware realsense_d425i.launch.py
ros2 launch service_robot_hardware scout_mini_base.launch.py
ros2 launch service_robot_hardware mid360.launch.py
ros2 launch service_robot_hardware piper_arm.launch.py
```

如果外部驱动没有安装，launch 会打印明确提示并安全退出，不影响仿真 demo。

## Point-LIO / Fast-LIO 接入入口

本仓库提供服务机器人 LIO 参数模板：

```bash
ros2 launch service_robot_lio point_lio.launch.py
ros2 launch service_robot_lio fast_lio.launch.py
```

如果没有安装外部 `point_lio` 或 `fast_lio` ROS2 包，launch 会打印提示并安全退出。完整 LIO 需要 3D LiDAR、IMU、外参和 rosbag/实机数据。

## TEB 接入入口

当前已验证 Nav2 默认使用 DWB。TEB 作为可选 controller 插件模板保存在：

```text
ros2_ws/src/service_robot_navigation/config/nav2_teb_params.yaml
```

检查入口：

```bash
ros2 launch service_robot_navigation teb_navigation.launch.py
```

要实际启用 TEB，需要工作空间中存在导出 `teb_local_planner::TebLocalPlannerROS` 的 ROS2 包。

## MoveIt2 / Piper / UMI 接入入口

当前 `service_robot_manipulation` 提供 MoveIt2/Piper/UMI 接入入口和明确依赖提示：

```bash
ros2 launch service_robot_manipulation manipulation.launch.py robot_model:=piper
```

已验证的无 GUI MoveIt2 demo：

```bash
ros2 launch service_robot_manipulation manipulation.launch.py demo_mode:=panda
```

该模式使用 ROS2 Humble apt 中的 Panda MoveIt 资源启动 `move_group`，用于证明 MoveIt2 框架和规划管线可启动。完整服务机器人/Piper/UMI 抓取闭环还需要对应的 `service_robot_moveit_config`、SRDF、controllers 和实际机械臂/仿真控制器。

## Docker

```bash
docker build -f docker/Dockerfile -t service-robot:humble .
docker run --rm -it service-robot:humble
```

GUI 运行需要额外配置 X11，详见 [docker/README.md](docker/README.md)。

## 已知限制

- MoveIt2 Panda `move_group` demo 已完成无 GUI 启动验证；服务机器人/Piper/UMI 专用 MoveIt 配置和抓取闭环仍需外部硬件或仿真控制器。
- Point-LIO / Fast-LIO 有接入入口和参数模板；当前 demo 已生成 MID360 风格仿真 PointCloud2/IMU rosbag，真实 LIO 闭环仍需实机外参与现场数据。
- TEB 有 Nav2 controller 参数模板，但未作为默认 Nav2 controller 验证；当前默认 Nav2 使用 DWB。
- 没有提交 YOLO 权重、训练数据集、真实机器人驱动或比赛现场数据。
- 外部厂商驱动位于 `external_ws/src`，默认不提交到 Git。

## Roadmap

优先级见 [docs/roadmap.md](docs/roadmap.md)：

1. 完善任务状态机：识别、导航、到达、分拣、返回。
2. 接入真实 YOLO 模型并保存验证图像/日志。
3. 生成服务机器人/Piper/UMI 专用 MoveIt2 配置，并接入仿真或实机控制器。
4. 如有 3D LiDAR/IMU 数据，再单独接入 Point-LIO 或 Fast-LIO。

## Demo 证据

仿真截图、短 rosbag 记录和运行日志放在 `assets/demo_runs/`。生成物可重新运行脚本获得，`.gitignore` 会避免提交大体积 bag 数据。
