#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
    
from plant_bot.hardware.gpio_wrapper import SoilProbePlatform

class SoilProbeNode(Node):
    def __init__(self):
        super().__init__('soil_probe_node')
        self.probe = SoilProbePlatform()
        self.subscription = self.create_subscription(String, 'soil_probe/command', self.cmd_callback, 10)
        self.publisher_ = self.create_publisher(Float32, 'soil_probe/moisture', 10)
        self.get_logger().info("Toprak Nem Prob Nodu baslatildi.")

    def cmd_callback(self, msg: String):
        if msg.data == "MEASURE":
            self.probe.probe_down()
            # Basitlik amacli prototipte delay eklenmistir. (Gercegi Action Server olmalı)
            import time
            time.sleep(2) 
            val = self.probe.read_moisture()
            self.probe.probe_up()
            
            pub_msg = Float32()
            pub_msg.data = val
            self.publisher_.publish(pub_msg)
            self.get_logger().info(f"Nem olculdu ve yayinlandi: {val}")

def main(args=None):
    rclpy.init(args=args)
    node = SoilProbeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
