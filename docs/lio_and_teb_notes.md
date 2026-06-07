# Point-LIO / Fast-LIO / TEB 说明

## Point-LIO / Fast-LIO

Point-LIO 和 Fast-LIO 通常需要：

- 3D LiDAR 点云 topic
- IMU topic
- LiDAR-IMU 外参
- 时间同步
- 实机或 rosbag 数据

当前仓库已在 Gazebo 中提供 2D `/scan`、RGB `/camera/image_raw`，并新增 MID360 风格 `/livox/lidar` PointCloud2 和 `/livox/imu` IMU 仿真输入。仓库已提供 `service_robot_lio` 包、Point-LIO/Fast-LIO 参数模板和 launch 入口；如果外部 LIO 包不存在，launch 会给出提示并安全退出。

当前已新增：

- `service_robot_lio`
- `config/point_lio_service_robot.yaml`
- `config/fast_lio_service_robot.yaml`
- `launch/point_lio.launch.py`
- `launch/fast_lio.launch.py`

已生成本地验证记录：

- `assets/demo_runs/latest/rosbag_nav_task`
- `assets/demo_runs/latest/rosbag_info.txt`

## TEB

当前仓库 Nav2 使用 DWB 局部规划器，并已验证 Humble 插件加载。TEB 不是 Nav2 Humble 默认局部规划器；仓库已提供 `nav2_teb_params.yaml` 作为 controller 参数模板，需要外部 `teb_local_planner` 插件包才能真正启用。

当前仓库已提供：

- Navigation2、DWB、NavFn、AMCL、SLAM Toolbox 验证结果
- TEB 参数模板和 launch 入口
- Point-LIO/Fast-LIO 参数模板和 launch 入口

完整实机闭环需要真实 MID360/IMU rosbag、外参和对应驱动。当前仓库提供仿真输入、参数模板和可运行验证记录。
