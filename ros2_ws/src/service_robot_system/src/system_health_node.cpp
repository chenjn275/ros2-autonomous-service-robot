#include <chrono>
#include <memory>
#include <sstream>
#include <string>

#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_srvs/srv/trigger.hpp"

using namespace std::chrono_literals;

class SystemHealthNode : public rclcpp::Node
{
public:
  SystemHealthNode()
  : Node("system_health_node")
  {
    timeout_sec_ = declare_parameter<double>("timeout_sec", 2.0);

    health_pub_ = create_publisher<std_msgs::msg::String>("/system/health", 10);
    scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
      "/scan", 10,
      [this](sensor_msgs::msg::LaserScan::SharedPtr) {
        last_scan_time_ = now();
      });
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/odom", 10,
      [this](nav_msgs::msg::Odometry::SharedPtr) {
        last_odom_time_ = now();
      });
    cmd_vel_sub_ = create_subscription<geometry_msgs::msg::Twist>(
      "/cmd_vel", 10,
      [this](geometry_msgs::msg::Twist::SharedPtr) {
        last_cmd_vel_time_ = now();
      });

    health_service_ = create_service<std_srvs::srv::Trigger>(
      "/system/health_check",
      [this](
        const std::shared_ptr<std_srvs::srv::Trigger::Request>,
        std::shared_ptr<std_srvs::srv::Trigger::Response> response) {
        response->success = is_healthy();
        response->message = make_status_json();
      });

    timer_ = create_wall_timer(1s, [this]() {
      std_msgs::msg::String msg;
      msg.data = make_status_json();
      health_pub_->publish(msg);
    });
  }

private:
  bool fresh(const rclcpp::Time & stamp) const
  {
    if (stamp.nanoseconds() == 0) {
      return false;
    }
    const double age = (now() - stamp).seconds();
    return age >= 0.0 && age <= timeout_sec_;
  }

  bool is_healthy() const
  {
    return fresh(last_scan_time_) && fresh(last_odom_time_);
  }

  std::string make_status_json() const
  {
    const bool scan_ok = fresh(last_scan_time_);
    const bool odom_ok = fresh(last_odom_time_);
    const bool cmd_vel_recent = fresh(last_cmd_vel_time_);

    std::ostringstream stream;
    stream << "{"
           << "\"healthy\":" << (scan_ok && odom_ok ? "true" : "false") << ","
           << "\"scan_ok\":" << (scan_ok ? "true" : "false") << ","
           << "\"odom_ok\":" << (odom_ok ? "true" : "false") << ","
           << "\"cmd_vel_recent\":" << (cmd_vel_recent ? "true" : "false") << ","
           << "\"timeout_sec\":" << timeout_sec_
           << "}";
    return stream.str();
  }

  double timeout_sec_{2.0};
  rclcpp::Time last_scan_time_{0, 0, RCL_ROS_TIME};
  rclcpp::Time last_odom_time_{0, 0, RCL_ROS_TIME};
  rclcpp::Time last_cmd_vel_time_{0, 0, RCL_ROS_TIME};

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr health_pub_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr health_service_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SystemHealthNode>());
  rclcpp::shutdown();
  return 0;
}
