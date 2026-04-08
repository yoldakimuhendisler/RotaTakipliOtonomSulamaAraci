#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random

class WaterLevelNode(Node):
    def __init__(self):
        super().__init__('water_level_node')
        self.publisher_ = self.create_publisher(Float32, 'water_tank/level', 10)
        self.timer = self.create_timer(10.0, self.timer_callback)
        self.level = 5.0 # Varsayilan tank: 5 Litre
        self.get_logger().info("Su Seviye Tespiti Nodu baslatildi.")

    def timer_callback(self):
        msg = Float32()
        msg.data = self.level
        self.publisher_.publish(msg)
        if self.level < 0.5:
             self.get_logger().warn("SU SEVIYESI COK DUSUK! Tanki doldurun.")

def main(args=None):
    rclpy.init(args=args)
    node = WaterLevelNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
