# 运行手册

## 1. 构建

```bash
bash scripts/install_deps.sh
bash scripts/build.sh
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
```

## 2. RViz 模型

无 GUI 验证：

```bash
ros2 launch service_robot_bringup display.launch.py use_rviz:=false
```

有 GUI：

```bash
ros2 launch service_robot_bringup display.launch.py
```

## 3. Gazebo 仿真

Headless：

```bash
ros2 launch service_robot_simulation gazebo.launch.py gui:=false
```

检查话题：

```bash
ros2 topic info /scan
ros2 topic info /odom
ros2 topic info /camera/image_raw
ros2 topic info /cmd_vel
```

## 4. SLAM

```bash
ros2 launch service_robot_localization slam.launch.py
```

需要同时存在 `/scan`、`/tf`、`/odom`。

## 5. Navigation2

```bash
ros2 launch service_robot_navigation navigation.launch.py
```

单独启动 Nav2 时等待 `odom -> base_footprint` 是正常现象；完整验证需要同时运行 Gazebo 或真实底盘。

## 6. 感知节点

二维码：

```bash
ros2 launch service_robot_perception qr_detection.launch.py
```

YOLO no-model：

```bash
ros2 launch service_robot_perception yolo_detection.launch.py
```

YOLO 模型：

```bash
ros2 launch service_robot_perception yolo_detection.launch.py model_path:=/path/to/model.pt
```

## 7. rosbag

```bash
bash scripts/record_demo_bag.sh
```

rosbag 输出到 `bags/`，默认不提交到 Git。
