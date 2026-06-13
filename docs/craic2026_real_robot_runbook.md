# CRAIC2026 实车自动比赛运行手册

目标：所有 ROS 节点都跑在车载 NUC 上，笔记本只通过 NoMachine/SSH 控制 NUC。校园网只用于远程桌面，不参与 ROS 多机通信；NUC 上设置 `ROS_LOCALHOST_ONLY=1`，避免校园网 DDS 干扰。

当前代码已经完成：

- D 区物品 YOLO 检测：`meat_001`、`vegetable_002`、`fruit_003`、`drink_004`
- E 区二维标记模板匹配：`001`、`002`、`003`、`004`
- 雷达接入：MID360 驱动由 NUC 启动，默认点云 `/livox/lidar`，导航默认检查 `/scan`
- 类别到盒子映射：肉类到 `001`，蔬菜到 `002`，水果到 `003`，饮料到 `004`
- Piper 固定示教轨迹服务：`pick`、`place_001`、`place_002`、`place_003`、`place_004`
- Mission Commander 自动流程：B/C/E 扫码/D 抓取/E 投放/F 充电区/返回起点
- NUC 一键入口：`scripts/nuc_start_competition.sh`

实车前必须现场生成的数据：

- E 区四个真实标记模板图：`marker_001.png` 到 `marker_004.png`
- Piper 真实抓放关节位姿：`home_safe`、D 区抓取点、E 区四个放置点
- 真实地图和所有比赛 waypoint 的 `x/y/yaw`

只要这三类数据没有填完，严格预检会失败，并且正式启动脚本不会放行。

## 1. NUC 首次准备

在 NUC 上执行：

```bash
cd /home/chen/ros2-autonomous-service-robot
sudo apt update
sudo apt install -y tmux can-utils net-tools iproute2
```

如果依赖还没装过：

```bash
cd /home/chen/ros2-autonomous-service-robot
bash scripts/install_deps.sh
```

构建：

```bash
cd /home/chen/ros2-autonomous-service-robot
bash scripts/nuc_build.sh
```

每个新终端都使用同一组环境：

```bash
cd /home/chen/ros2-autonomous-service-robot/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=26
export ROS_LOCALHOST_ONLY=1
```

## 2. 校园网和远程控制规划

NUC 和笔记本都连校园网。NUC 上查 IP：

```bash
hostname -I
ip addr
```

笔记本 NoMachine 连接 NUC 的校园网 IP。SSH 备用：

```bash
ssh chen@NUC_IP
```

ROS 不跨机器通信，所有 ROS 命令都在 NUC 上跑。笔记本只看远程桌面、RViz、终端和日志。

## 3. 确认硬件接口

查看 CAN：

```bash
ip link show | grep can
```

如果底盘是 `can0`，Piper 是 `can1`：

```bash
sudo ip link set can0 down || true
sudo ip link set can1 down || true
sudo ip link set can0 type can bitrate 500000
sudo ip link set can1 type can bitrate 1000000
sudo ip link set can0 up
sudo ip link set can1 up
ip -details link show can0
ip -details link show can1
```

如果现场只有一个 CAN 口，要先确认底盘和 Piper 是否真的共用同一 CAN。不是共用就不能把两个都写成 `can0`。

检查相机：

```bash
ros2 launch service_robot_hardware realsense_d425i.launch.py camera_name:=d425i
```

另开终端：

```bash
ros2 topic list | grep -E 'image_raw|color/image'
ros2 topic hz /d425i/color/image_raw
```

如果相机 topic 不是 `/d425i/color/image_raw`，修改：

```bash
gedit /home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_bringup/config/craic2026_nuc.yaml
```

改：

```yaml
hardware:
  image_topic: /实际/image/topic
```

雷达 topic 也在同一个文件里确认：

```yaml
hardware:
  lidar_pointcloud_topic: /livox/lidar
  lidar_imu_topic: /livox/imu
  scan_topic: /scan
```

检查激光：

```bash
ros2 launch service_robot_hardware mid360.launch.py
ros2 topic list | grep -E 'scan|points|livox'
ros2 topic hz /scan
```

当前 Nav2 配置使用 `/scan`。如果 MID360 只发点云没有 `/scan`，必须现场增加点云转 LaserScan 或改 Nav2 costmap 参数；否则导航不能进入正式比赛。

## 4. 捕获 E 区模板

先启动相机：

```bash
cd /home/chen/ros2-autonomous-service-robot/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=26
export ROS_LOCALHOST_ONLY=1
ros2 launch service_robot_hardware realsense_d425i.launch.py camera_name:=d425i
```

把车停在 E 区扫码位置，让四个标记分别清晰占据画面。另开终端，按实际相机 topic 保存模板：

```bash
cd /home/chen/ros2-autonomous-service-robot/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=26
export ROS_LOCALHOST_ONLY=1

ros2 run service_robot_perception image_snapshot --ros-args \
  -p image_topic:=/d425i/color/image_raw \
  -p output_path:=/home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_perception/config/marker_001.png
```

重复保存：

```bash
ros2 run service_robot_perception image_snapshot --ros-args -p image_topic:=/d425i/color/image_raw -p output_path:=/home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_perception/config/marker_002.png
ros2 run service_robot_perception image_snapshot --ros-args -p image_topic:=/d425i/color/image_raw -p output_path:=/home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_perception/config/marker_003.png
ros2 run service_robot_perception image_snapshot --ros-args -p image_topic:=/d425i/color/image_raw -p output_path:=/home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_perception/config/marker_004.png
```

编辑模板配置：

```bash
gedit /home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_perception/config/custom_markers.yaml
```

给每个 marker 加 `template_path`：

```yaml
markers:
  - id: "001"
    label: meat
    place_zone: e_bin_001
    template_path: marker_001.png
  - id: "002"
    label: vegetable
    place_zone: e_bin_002
    template_path: marker_002.png
  - id: "003"
    label: fruit
    place_zone: e_bin_003
    template_path: marker_003.png
  - id: "004"
    label: drink
    place_zone: e_bin_004
    template_path: marker_004.png
```

测试模板识别：

```bash
ros2 launch service_robot_perception craic2026_perception.launch.py \
  image_topic:=/d425i/color/image_raw \
  yolo_model_path:=/home/chen/model_backup/craic_items_baseline_best.pt \
  yolo_confidence:=0.45 \
  marker_match_threshold:=0.65
```

另开终端：

```bash
ros2 topic echo /perception/custom_marker/result
ros2 topic echo /perception/yolo/detections
```

通过标准：

- E 区能稳定看到 `001`、`002`、`003`、`004`
- D 区物品能输出 `meat_001`、`vegetable_002`、`fruit_003` 或 `drink_004`

## 5. 记录 Piper 真实抓放轨迹

先启动 Piper 驱动：

```bash
cd /home/chen/ros2-autonomous-service-robot/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=26
export ROS_LOCALHOST_ONLY=1

ros2 launch service_robot_manipulation piper_real_manipulation.launch.py \
  can_port:=can1 \
  auto_enable:=true \
  require_calibrated:=false \
  dry_run:=true
```

如果 Piper 接在 `can0`：

```bash
ros2 launch service_robot_manipulation piper_real_manipulation.launch.py \
  can_port:=can0 \
  auto_enable:=true \
  require_calibrated:=false \
  dry_run:=true
```

确认反馈：

```bash
ros2 topic echo /joint_states_feedback --once
```

把机械臂手动/示教移动到对应姿态，每到一个姿态保存一次：

```bash
cd /home/chen/ros2-autonomous-service-robot
bash scripts/nuc_record_piper_pose.sh home_safe
bash scripts/nuc_record_piper_pose.sh d_pre_grasp
bash scripts/nuc_record_piper_pose.sh d_grasp
bash scripts/nuc_record_piper_pose.sh d_lift
bash scripts/nuc_record_piper_pose.sh e_pre_place_001
bash scripts/nuc_record_piper_pose.sh e_place_001
bash scripts/nuc_record_piper_pose.sh e_pre_place_002
bash scripts/nuc_record_piper_pose.sh e_place_002
bash scripts/nuc_record_piper_pose.sh e_pre_place_003
bash scripts/nuc_record_piper_pose.sh e_place_003
bash scripts/nuc_record_piper_pose.sh e_pre_place_004
bash scripts/nuc_record_piper_pose.sh e_place_004 --calibrated
```

最后一个命令带 `--calibrated`，会把 `metadata.calibrated` 置为 `true`。

先 dry-run 服务：

```bash
ros2 launch service_robot_manipulation piper_fixed_sequences.launch.py \
  require_calibrated:=true \
  dry_run:=true
```

另开终端调用：

```bash
ros2 service call /manipulation/piper/pick std_srvs/srv/Trigger {}
ros2 service call /manipulation/piper/place_001 std_srvs/srv/Trigger {}
ros2 service call /manipulation/piper/place_002 std_srvs/srv/Trigger {}
ros2 service call /manipulation/piper/place_003 std_srvs/srv/Trigger {}
ros2 service call /manipulation/piper/place_004 std_srvs/srv/Trigger {}
```

确认 dry-run 都成功后，才跑真实机械臂动作：

```bash
ros2 launch service_robot_manipulation piper_real_manipulation.launch.py \
  can_port:=can1 \
  auto_enable:=true \
  require_calibrated:=true \
  dry_run:=false
```

逐个调用服务。通过标准：

- `pick` 能安全抓起 D 区物品
- `place_001` 到 `place_004` 能分别放到四个盒子
- 任意轨迹擦碰、过低、过高、夹爪方向反，必须重新示教对应 pose

## 6. 填真实导航点

启动底盘、激光、Nav2 和 RViz 后，在地图坐标系记录这些点：

```text
zone_b_visit
zone_c_visit
zone_e_scan_markers
zone_d_pick_table
zone_e_place_shelf
zone_f_charge
return_start_area
```

编辑任务配置：

```bash
gedit /home/chen/ros2-autonomous-service-robot/ros2_ws/src/Venom_VNV/venom_mission_commander/config/craic2026_home_sorting_real.yaml
```

把每个 waypoint 的 `x/y/yaw` 改成真实地图位姿。不要保留全 0。

如果地图不是 `demo_map.yaml`，修改：

```bash
gedit /home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_bringup/config/craic2026_nuc.yaml
```

改：

```yaml
competition:
  map: /真实/map.yaml
```

单点导航先测：

```bash
ros2 launch service_robot_navigation navigation.launch.py \
  map:=/真实/map.yaml \
  params_file:=/home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_navigation/config/nav2_params.yaml \
  use_sim_time:=false
```

RViz 里给 `2D Pose Estimate`，再用 `Nav2 Goal` 测每个点。通过标准：

- 每个 waypoint 都能到
- E 扫码点相机能看全四个标记
- D 抓取点机械臂能碰到物品
- E 放置点机械臂能碰到四个盒子

## 7. 严格预检

构建一次：

```bash
cd /home/chen/ros2-autonomous-service-robot
bash scripts/nuc_build.sh
```

跑总预检：

```bash
cd /home/chen/ros2-autonomous-service-robot
bash scripts/nuc_preflight.sh
```

也可以分开跑：

```bash
cd /home/chen/ros2-autonomous-service-robot/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=26
export ROS_LOCALHOST_ONLY=1

ros2 run service_robot_perception craic_preflight_check -- --strict
ros2 run service_robot_manipulation piper_sequence_validator -- --strict
ros2 run venom_mission_commander craic_real_config_check -- --strict
ros2 run service_robot_bringup craic_nuc_preflight -- --config src/service_robot_bringup/config/craic2026_nuc.yaml --strict
```

通过标准：全部输出 `OK`。任何一个失败，都不要启动正式自动比赛。

## 8. 正式比赛启动

确认 NUC 配置：

```bash
gedit /home/chen/ros2-autonomous-service-robot/ros2_ws/src/service_robot_bringup/config/craic2026_nuc.yaml
```

正式配置应为：

```yaml
runtime:
  require_piper_calibrated: true
  piper_dry_run: false
  piper_start_driver: true
  mission_use_nav: true
  start_hardware: true
  start_navigation: true
  start_perception: true
  start_manipulation: true
  start_mission: true
```

一键启动：

```bash
cd /home/chen/ros2-autonomous-service-robot
bash scripts/nuc_start_competition.sh
```

脚本会先跑严格预检。预检通过后创建 tmux：

```bash
tmux attach -t craic_competition
```

窗口：

- `preflight`：严格预检结果
- `competition`：完整比赛 launch 日志
- `runtime-check`：topic/service/action 是否就绪

tmux 常用操作：

```text
Ctrl-b n        下一个窗口
Ctrl-b p        上一个窗口
Ctrl-b d        退出 tmux 但不停止程序
```

停止整场：

```bash
cd /home/chen/ros2-autonomous-service-robot
bash scripts/nuc_stop_competition.sh
```

## 9. 现场排错顺序

看 ROS 节点：

```bash
ros2 node list
```

看关键 topic：

```bash
ros2 topic hz /d425i/color/image_raw
ros2 topic hz /scan
ros2 topic echo /perception/yolo/detections --once
ros2 topic echo /perception/custom_marker/result --once
ros2 topic echo /joint_states_feedback --once
```

看 Piper 服务：

```bash
ros2 service list | grep /manipulation/piper
```

看 Nav2 action：

```bash
ros2 action list | grep navigate_to_pose
```

跑运行时检查：

```bash
ros2 run service_robot_bringup craic_runtime_check -- \
  --topic /d425i/color/image_raw:Image \
  --topic /perception/yolo/detections:String \
  --topic /perception/custom_marker/result:String \
  --topic /joint_states_feedback:JointState \
  --topic /scan:LaserScan \
  --service /manipulation/piper/pick \
  --service /manipulation/piper/place_001 \
  --service /manipulation/piper/place_002 \
  --service /manipulation/piper/place_003 \
  --service /manipulation/piper/place_004 \
  --nav2-action \
  --timeout-sec 45.0
```

如果只想做不动硬件的软件联调，临时改 `craic2026_nuc.yaml`：

```yaml
runtime:
  piper_dry_run: true
  piper_start_driver: false
  mission_use_nav: false
  start_hardware: false
  start_navigation: false
  start_perception: false
```

然后手动指定 dry-run mission：

```bash
cd /home/chen/ros2-autonomous-service-robot/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=26
export ROS_LOCALHOST_ONLY=1

ros2 launch service_robot_bringup craic2026_competition.launch.py \
  start_hardware:=false \
  start_navigation:=false \
  start_perception:=false \
  start_manipulation:=true \
  start_mission:=true \
  piper_start_driver:=false \
  require_piper_calibrated:=false \
  piper_dry_run:=true \
  mission_use_nav:=false \
  mission_config:=/home/chen/ros2-autonomous-service-robot/ros2_ws/src/Venom_VNV/venom_mission_commander/config/craic2026_home_sorting_service_dryrun.yaml
```
