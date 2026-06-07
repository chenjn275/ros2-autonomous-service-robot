# 验证记录

本文档记录当前仓库在 Ubuntu 22.04 + ROS2 Humble 虚拟机中的实际验证结果。README 中的“已验证”描述以本文档为准。

## 环境

- Ubuntu 22.04.5 LTS
- ROS2 Humble
- Python 3.10.12
- colcon 可用
- rosdep 可用，但当前 rosdep 源中存在部分 `raw.gitmirror.com` DNS 失败；已通过 apt 直接安装关键 ROS 依赖。

已安装并验证可见的关键 ROS 包：

- `gazebo_ros`
- `nav2_bringup`
- `slam_toolbox`
- `rviz2`
- `robot_state_publisher`
- `joint_state_publisher`
- `joint_state_publisher_gui`
- `cv_bridge`
- `image_transport`
- `rosbag2`
- `moveit_ros_move_group`
- `moveit_resources_panda_description`
- `moveit_resources_panda_moveit_config`

## 已通过检查

- `bash scripts/build.sh`：11 个 `service_robot_*` 包全部构建通过。
- `bash scripts/check_python.sh`：Python 节点与 launch 文件语法检查通过。
- `ros2 pkg list | grep service_robot`：11 个包均可被 ROS2 识别。
- `xacro .../service_robot.urdf.xacro > /tmp/service_robot.urdf`：xacro 展开成功。
- `check_urdf /tmp/service_robot.urdf`：URDF XML 解析成功。
- `ros2 launch ... --show-args`：display、demo、gazebo、slam、navigation、qr、yolo、task、Point-LIO、Fast-LIO、TEB、manipulation、system launch 参数检查通过。
- `timeout 8s ros2 launch service_robot_bringup display.launch.py use_rviz:=false`：`robot_state_publisher` 与零位关节状态发布器可启动。
- `ros2 launch service_robot_bringup demo.launch.py gui:=false`：一键 demo 可拉起 `robot_state_publisher`、`gzserver`、`spawn_entity.py`、QR、YOLO、C++ health、task commander；可见 `/scan`、`/odom`、`/cmd_vel`、`/camera/image_raw`、`/livox/lidar`、`/livox/imu`、`/system/health` 等话题。
- `ros2 launch service_robot_simulation gazebo.launch.py gui:=false`：Gazebo headless 可启动并发布关键话题。
- `ros2 launch service_robot_perception qr_detection.launch.py`：节点订阅/发布接口验证通过。
- `ros2 launch service_robot_perception yolo_detection.launch.py`：no-model 模式接口验证通过。
- `timeout 10s ros2 launch service_robot_localization slam.launch.py`：SLAM Toolbox 节点启动并加载 Ceres solver。
- `ros2 launch service_robot_navigation navigation.launch.py`：Nav2 生命周期节点、map_server、AMCL、planner、controller、behavior 和 BT navigator 加载成功；默认验证链路为轻量 Nav2 栈，不启动 velocity smoother 或 waypoint follower。
- `timeout 12s ros2 launch service_robot_tasks task_commander.launch.py`：任务流程节点可读取 YAML，并以 mock navigation 跑完服务流程。
- `ros2 launch service_robot_lio point_lio.launch.py --show-args`：Point-LIO 接入入口参数检查通过。
- `ros2 launch service_robot_lio fast_lio.launch.py --show-args`：Fast-LIO 接入入口参数检查通过。
- `ros2 launch service_robot_navigation teb_navigation.launch.py --show-args`：TEB 参数模板入口检查通过。
- `ros2 launch service_robot_manipulation manipulation.launch.py --show-args`：MoveIt2/Piper 接入入口检查通过。
- `timeout 12s ros2 launch service_robot_manipulation manipulation.launch.py demo_mode:=panda`：Panda `move_group` 启动成功，MoveIt2 日志输出 `You can start planning now!`；`timeout` 返回 124 是主动截断。
- `ros2 launch service_robot_system system_health.launch.py --show-args`：C++ 系统健康监控 launch 参数检查通过。
- `ros2 launch service_robot_hardware hardware_bringup.launch.py --show-args`：D425i、Scout Mini、MID360、Piper、NUC 硬件总入口参数检查通过。
- `ros2 launch service_robot_hardware realsense_d425i.launch.py --show-args`：RealSense D425i wrapper 参数检查通过。
- `ros2 launch service_robot_hardware scout_mini_base.launch.py --show-args`：Scout Mini wrapper 参数检查通过。
- `ros2 launch service_robot_hardware mid360.launch.py --show-args`：MID360 wrapper 参数检查通过。
- `ros2 launch service_robot_hardware piper_arm.launch.py --show-args`：Piper wrapper 参数检查通过。
- `bash scripts/capture_demo_evidence.sh`：生成 demo 截图、topic/node 列表和 rosbag 记录。
- `ros2 bag info assets/demo_runs/latest/rosbag_nav_task`：验证 bag 包含 `/livox/lidar`、`/livox/imu`、`/camera/image_raw`、`/scan`、`/odom`、`/tf`、`/tasks/status`、`/system/health` 等话题。

## Gazebo 话题验证

Headless Gazebo 启动后检查结果：

- `/scan`：`sensor_msgs/msg/LaserScan`，Publisher count: 1
- `/odom`：`nav_msgs/msg/Odometry`，Publisher count: 1
- `/camera/image_raw`：`sensor_msgs/msg/Image`，Publisher count: 1
- `/cmd_vel`：`geometry_msgs/msg/Twist`，Subscription count: 1

## 感知节点接口

QR 节点：

- 订阅：`/camera/image_raw`
- 发布：`/perception/qr/result`、`/perception/qr/annotated`

YOLO 节点：

- 订阅：`/camera/image_raw`
- 发布：`/perception/yolo/detections`、`/perception/yolo/annotated`
- 默认 `model_path` 为空时进入 no-model 模式，只发布空 detections，并在日志中说明。

## 系统健康节点接口

`service_robot_system` 是 C++/ament_cmake 包：

- 订阅：`/scan`
- 订阅：`/odom`
- 订阅：`/cmd_vel`
- 发布：`/system/health`
- 服务：`/system/health_check`，类型为 `std_srvs/srv/Trigger`

## Demo Evidence

`assets/demo_runs/latest` 中本地生成了：

- `demo_camera_frame.png`：Gazebo 相机帧，640x480。
- `topic_list.txt` / `node_list.txt`：demo 运行时话题和节点列表。
- `rosbag_nav_task/metadata.yaml` 和本地 `.db3`：短 rosbag 记录，`.db3` 被 Git 忽略。
- `rosbag_info.txt`：bag 摘要。

Bag 验证摘要：

- 总时长：83.09 秒
- 总消息数：4870
- `/livox/lidar`：191 条 `sensor_msgs/msg/PointCloud2`
- `/livox/imu`：1558 条 `sensor_msgs/msg/Imu`
- `/camera/image_raw`：201 条 `sensor_msgs/msg/Image`
- `/scan`：193 条 `sensor_msgs/msg/LaserScan`
- `/odom`：1951 条 `nav_msgs/msg/Odometry`
- `/tasks/status`：26 条 `std_msgs/msg/String`

## 已知限制

- Nav2 单独启动时会等待 `odom -> base_footprint` TF；需要与 Gazebo 或真实底盘同时运行。
- MoveIt2 Panda `move_group` demo 已在无 GUI 环境启动验证；服务机器人/Piper/UMI 专用 MoveIt 配置和真实抓取闭环仍未随仓库公开。
- Point-LIO、Fast-LIO、TEB 已提供接入入口和模板；当前仓库已生成 MID360 风格仿真 PointCloud2/IMU rosbag，可用于接口级验证。真实 LIO 闭环仍需实机 MID360/IMU 外参与现场数据。
- 本仓库不包含模型权重、训练数据集、真实机器人驱动或比赛现场数据。
