from pathlib import Path

from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from launch.actions import IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import AnyLaunchDescriptionSource


def include_optional_launch(package_name, candidates, launch_arguments=None, missing_hint=""):
    try:
        share_dir = Path(get_package_share_directory(package_name))
    except PackageNotFoundError:
        return [
            LogInfo(
                msg=(
                    f"Optional hardware driver package '{package_name}' is not installed. "
                    f"{missing_hint}"
                )
            )
        ]

    for candidate in candidates:
        launch_path = share_dir / candidate
        if launch_path.is_file():
            return [
                IncludeLaunchDescription(
                    AnyLaunchDescriptionSource(str(launch_path)),
                    launch_arguments=(launch_arguments or {}).items(),
                )
            ]

    return [
        LogInfo(
            msg=(
                f"Package '{package_name}' is installed, but none of these launch files "
                f"were found: {', '.join(candidates)}. {missing_hint}"
            )
        )
    ]
