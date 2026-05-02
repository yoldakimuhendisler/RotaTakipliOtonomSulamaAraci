#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from plant_bot.hardware.gpio_wrapper import WaterPump

class WateringNode(Node):
    def __init__(self):
        super().__init__('watering_node')
        self.pump = WaterPump()
        self.subscription = self.create_subscription(Float32, 'watering/command_duration', self.cmd_callback, 10)
        self.get_logger().info("Sulama Pompasi Nodu baslatildi.")

    def cmd_callback(self, msg: Float32):
        try:
            sec = msg.data
            if sec <= 0:
                self.get_logger().warning("Gecersiz sulama suresi (<=0) alindi, islem iptal ediliyor.")
                return
            
            self.get_logger().info(f"{sec} saniyelik sulama komutu alindi.")
            self.pump.run_pump(sec)
            self.get_logger().info("Sulama islemi basariyla bitti.")
        except Exception as e:
            self.get_logger().error(f"Sulama isleminde kritik hata: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = WateringNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
