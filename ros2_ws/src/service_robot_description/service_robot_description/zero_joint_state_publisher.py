import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ZeroJointStatePublisher(Node):
    def __init__(self):
        super().__init__("zero_joint_state_publisher")
        self.declare_parameter("joint_names", ["left_wheel_joint", "right_wheel_joint"])
        self.joint_names = [
            str(name)
            for name in self.get_parameter("joint_names").get_parameter_value().string_array_value
        ]
        self.publisher = self.create_publisher(JointState, "joint_states", 10)
        self.timer = self.create_timer(0.05, self.publish_joint_states)

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [0.0] * len(self.joint_names)
        msg.velocity = [0.0] * len(self.joint_names)
        msg.effort = [0.0] * len(self.joint_names)
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ZeroJointStatePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
