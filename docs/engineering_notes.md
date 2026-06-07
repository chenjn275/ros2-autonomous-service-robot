# 工程化说明

本仓库采用 `service_robot_*` 多包结构组织，外部厂商驱动放在被 Git 忽略的 `external_ws/src`，不进入仓库历史。

## 包组织

- `service_robot_bringup`
- `service_robot_description`
- `service_robot_simulation`
- `service_robot_localization`
- `service_robot_navigation`
- `service_robot_perception`
- `service_robot_manipulation`
- `service_robot_tasks`
- `service_robot_lio`
- `service_robot_system`
- `service_robot_hardware`

## 不提交内容

- `ros2_ws/build`
- `ros2_ws/install`
- `ros2_ws/log`
- `__pycache__`
- `.pyc`
- `bags`
- 模型权重
- 数据集

## 建议开发流程

```bash
bash scripts/build.sh
bash scripts/check_python.sh
xacro ros2_ws/src/service_robot_description/urdf/service_robot.urdf.xacro > /tmp/service_robot.urdf
check_urdf /tmp/service_robot.urdf
```

再按需运行 launch：

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 launch service_robot_simulation gazebo.launch.py gui:=false
```
