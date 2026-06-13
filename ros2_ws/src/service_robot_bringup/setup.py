from glob import glob
import os
from setuptools import setup

package_name = "service_robot_bringup"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/config", glob("config/*")),
        (
            f"share/{package_name}/scripts",
            [
                path
                for path in glob("scripts/*")
                if os.path.isfile(path)
            ],
        ),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/rviz", glob("rviz/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="chen",
    maintainer_email="user@example.com",
    description="Top-level launch files for the indoor service robot demo.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "craic_nuc_preflight = service_robot_bringup.craic_nuc_preflight:main",
            "craic_runtime_check = service_robot_bringup.craic_runtime_check:main",
        ],
    },
)
