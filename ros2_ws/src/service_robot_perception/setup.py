from glob import glob
from setuptools import setup

package_name = "service_robot_perception"

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
    description="Camera perception nodes for QR and YOLO detection.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "qr_detector = service_robot_perception.qr_detector:main",
            "yolo_detector = service_robot_perception.yolo_detector:main",
        ],
    },
)
