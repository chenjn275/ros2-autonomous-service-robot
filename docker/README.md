# Docker

Dockerfile 用于复现 ROS2 Humble 桌面开发环境，包含 RViz2、Gazebo Classic、Navigation2、SLAM Toolbox、cv_bridge、image_transport 和 rosbag2。

构建：

```bash
docker build -f docker/Dockerfile -t service-robot:humble .
```

运行无 GUI shell：

```bash
docker run --rm -it service-robot:humble
```

如果需要 RViz2/Gazebo GUI，需要额外映射 X11 或使用宿主机原生环境运行。当前仓库已在 Ubuntu 22.04 + ROS2 Humble 虚拟机原生环境验证基础 demo。
