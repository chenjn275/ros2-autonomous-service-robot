# 服务机器人任务流程设计

当前仓库的已验证能力适合支撑一个室内服务机器人基础 demo：

1. Gazebo 发布 `/scan`、`/odom`、`/camera/image_raw`。
2. SLAM Toolbox 或 AMCL/Nav2 使用 `/scan`、`/odom` 和 `/tf`。
3. QR 节点订阅 `/camera/image_raw`，发布二维码结果。
4. YOLO 节点订阅 `/camera/image_raw`，发布检测结果；无模型时发布空 detections。
5. Nav2 接收目标位姿后输出 `/cmd_vel`。
6. Gazebo 差速底盘插件订阅 `/cmd_vel` 并发布 `/odom`。

## 已实现任务流程节点

已新增 `service_robot_tasks` 包，节点职责如下：

- 订阅 `/perception/qr/result`
- 订阅 `/perception/yolo/detections`
- 调用 Nav2 `NavigateToPose` action
- 根据任务点配置执行“识别 -> 导航 -> 到达 -> 分拣 -> 返回”

默认 `use_nav:=false` 时使用 mock navigation，便于在没有 Nav2 的情况下验证任务流程。设置 `use_nav:=true` 时会调用 Nav2 action。

当前仓库尚未实现真实机械臂抓取，因此“分拣”是任务状态和日志模拟，不应写成已完成真实抓取。
