# Roadmap

## P0：基础闭环

- 已优化 Gazebo、Nav2、QR、YOLO、任务流程的分阶段启动顺序，降低虚拟机中 DDS 发现和 lifecycle 启动的资源竞争。
- 使用 `ros2 action send_goal /navigate_to_pose` 发送导航目标，验证机器人在 demo map 中运动。
- 增加 `service_robot_bringup demo.launch.py` 的一键 demo 参数。

## P1：感知与任务

- 为 YOLO 准备轻量模型，并在 README 中记录模型来源、类别和验证图像。
- 将二维码识别结果和 YOLO 结果统一成任务层输入。
- 增加任务状态机：识别、导航、到达、分拣、返回。

## P2：机械臂

- MoveIt2 Panda `move_group` demo 已验证，后续重点转为服务机器人/Piper/UMI 专用配置。
- 为服务机器人添加轻量机械臂 URDF/xacro 或导入实机使用的机械臂模型。
- 使用 MoveIt Setup Assistant 生成 SRDF、planning config、controllers 和 joint limits。
- 验证 RViz MotionPlanning 插件、一条轨迹规划和仿真/实机控制器执行。

## P3：定位扩展

- 保留 SLAM Toolbox 作为 2D 激光建图主线。
- Point-LIO/Fast-LIO 需要 3D LiDAR、IMU、点云 topic 和外参，不建议在没有传感器数据时伪实现。
- 若后续使用 3D LiDAR，应补充点云/IMU rosbag、外参和实机验证日志。

## P4：导航扩展

- 当前 Nav2 使用 DWB，本仓库已验证插件加载。
- TEB 在 ROS2 Humble 中不是 Nav2 默认插件，建议后续单独评估兼容包和维护状态。
- 若需要写 TEB，请先提供可运行 launch、参数、日志和对比结果。
