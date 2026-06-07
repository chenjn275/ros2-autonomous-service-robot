from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description():
    return LaunchDescription(
        [
            LogInfo(
                msg=(
                    "TEB is provided as an optional Nav2 controller parameter template in "
                    "service_robot_navigation/config/nav2_teb_params.yaml. Install/build a "
                    "ROS2 package exporting teb_local_planner::TebLocalPlannerROS, then merge "
                    "that controller override into the main Nav2 params before launching."
                )
            )
        ]
    )
