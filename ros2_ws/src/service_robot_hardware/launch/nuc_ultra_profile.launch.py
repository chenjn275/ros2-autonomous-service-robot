from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description():
    return LaunchDescription(
        [
            LogInfo(
                msg=(
                    "NUC Ultra is the onboard computer profile for this robot. "
                    "Use docs/hardware_setup.md for network, CAN, udev, and power checks."
                )
            )
        ]
    )
