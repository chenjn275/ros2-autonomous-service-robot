# MoveIt2 / Manipulation 模板边界

`service_robot_manipulation` 当前提供 MoveIt2/Piper/UMI 接入入口，并已验证 Panda `move_group` 无 GUI demo。该验证证明 MoveIt2 框架、planning pipeline 和 `move_group` 能启动；它不是服务机器人/Piper/UMI 的真实抓取闭环。

已验证入口：

```bash
ros2 launch service_robot_manipulation manipulation.launch.py demo_mode:=panda
```

如果要把服务机器人/Piper/UMI 的 MoveIt2 写成完整闭环，需要继续补齐：

1. 在 `service_robot_description` 中加入机械臂 URDF/xacro，或导入实机机械臂模型。
2. 使用 MoveIt Setup Assistant 生成 SRDF、kinematics、planning pipeline、controllers。
3. 新增 `service_robot_manipulation_moveit_config` 包。
4. 接入仿真或实机控制器。
5. 验证：

```bash
ros2 node list | grep move_group
ros2 action list | grep move_action
```

6. 在 RViz MotionPlanning 中完成至少一条规划，并保存日志或截图。

在完成以上步骤前，仓库提供的是 MoveIt2 Panda demo、Piper/UMI 接入入口和参数模板；真实机械臂抓取闭环需要专用模型、控制器和实机或仿真执行记录。
