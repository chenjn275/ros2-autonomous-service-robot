from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration

from service_robot_hardware.optional_launch import include_optional_launch


def launch_setup(context, *args, **kwargs):
    serial_no = LaunchConfiguration("serial_no")
    camera_name = LaunchConfiguration("camera_name")
    return include_optional_launch(
        "realsense2_camera",
        ["launch/rs_launch.py", "rs_launch.py"],
        {
            "serial_no": serial_no,
            "camera_name": camera_name,
            "enable_depth": "true",
            "enable_color": "true",
            "enable_gyro": "true",
            "enable_accel": "true",
            "unite_imu_method": "2",
            "align_depth.enable": "true",
            "depth_module.profile": "640x480x30",
            "rgb_camera.profile": "640x480x30",
        },
        "Install ros-humble-realsense2-camera or fetch IntelRealSense/realsense-ros.",
    )


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("serial_no", default_value=""),
            DeclareLaunchArgument("camera_name", default_value="d425i"),
            OpaqueFunction(function=launch_setup),
        ]
    )
