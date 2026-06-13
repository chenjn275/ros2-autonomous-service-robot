from glob import glob
from setuptools import setup

package_name = "service_robot_manipulation"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/config", glob("config/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="chen",
    maintainer_email="user@example.com",
    description="MoveIt2 integration entry points for the indoor service robot demo.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "piper_pose_recorder = service_robot_manipulation.piper_pose_recorder:main",
            "piper_sequence_executor = service_robot_manipulation.piper_sequence_executor:main",
            "piper_sequence_validator = service_robot_manipulation.piper_sequence_validator:main",
        ],
    },
)
