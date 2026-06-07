from glob import glob
from setuptools import setup

package_name = "service_robot_description"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/rviz", glob("rviz/*")),
        (f"share/{package_name}/urdf", glob("urdf/*")),
        (f"share/{package_name}/meshes", glob("meshes/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="chen",
    maintainer_email="user@example.com",
    description="Robot description, xacro model, and RViz display launch files.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "zero_joint_state_publisher = service_robot_description.zero_joint_state_publisher:main",
        ],
    },
)
