#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MotionControlNode(Node):
    def __init__(self):
        super().__init__('motion_control_node')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_callback,
            10
        )
        self.get_logger().info("Motion Control baslatildi. Motor suruculer bekleniyor.")

    def cmd_callback(self, msg: Twist):
        # Gerçek kodda burada PWM/I2C/Serial motor komutlari doner
        linear = msg.linear.x
        angular = msg.angular.z
        if linear != 0.0 or angular != 0.0:
            self.get_logger().debug(f"Motor Sürüş -> Ileri: {linear:.2f}, Dönüş: {angular:.2f}")

def main(args=None):
    rclpy.init(args=args)
    node = MotionControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
