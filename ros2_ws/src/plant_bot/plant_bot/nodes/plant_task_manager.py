#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
import time

class PlantTaskManager(Node):
    def __init__(self):
        super().__init__('plant_task_manager')
        self.state = "SEARCHING"
        self.subscription_ai = self.create_subscription(String, 'ai/detections', self.ai_callback, 10)
        
        self.probe_cmd_pub = self.create_publisher(String, 'soil_probe/command', 10)
        self.water_cmd_pub = self.create_publisher(Float32, 'watering/command_duration', 10)
        self.probe_res_sub = self.create_subscription(Float32, 'soil_probe/moisture', self.moisture_callback, 10)
        
        self.timer = self.create_timer(1.0, self.state_machine_loop)
        self.get_logger().info("Görev Yöneticisi (State Machine) başlatıldı. Durum: SEARCHING")
        self.target_found = False
        self.moisture_val = None

    def ai_callback(self, msg: String):
        if self.state == "SEARCHING":
            if "Plant" in msg.data and "success\": true" in msg.data.lower():
                self.target_found = True
                self.get_logger().info("Bitki tespit edildi! Durum: APPROACHING")
                self.state = "APPROACHING"

    def moisture_callback(self, msg: Float32):
        if self.state == "MEASURING":
            self.moisture_val = msg.data
            self.get_logger().info(f"Nem okundu: {self.moisture_val}%")
            if self.moisture_val < 40.0:
                self.get_logger().info("Nem yetersiz (<%40), sulama yapilacak.")
                self.state = "WATERING"
            else:
                self.get_logger().info("Nem yeterli, sulama yapilmayacak. Sonraki hedefe geciliyor.")
                self.state = "SEARCHING"
                self.target_found = False

    def state_machine_loop(self):
        if self.state == "APPROACHING":
            self.get_logger().info("Hedefe yaklaşılıyor...")
            # Sahte gecikme (Gercekte goal_reached event'ini bekler)
            time.sleep(2)
            self.state = "MEASURING"
            
            self.get_logger().info("Nem ölçme komutu gönderiliyor.")
            msg = String()
            msg.data = "MEASURE"
            self.probe_cmd_pub.publish(msg)
            
        elif self.state == "WATERING":
            self.get_logger().info("Sulama komutu gönderiliyor...")
            msg = Float32()
            msg.data = 3.0 # 3 saniye sula
            self.water_cmd_pub.publish(msg)
            
            # Sulamanin bitmesini bekle
            time.sleep(5) 
            self.state = "SEARCHING"
            self.target_found = False
            self.get_logger().info("Sulama bitti. Tekrar arayisa cikildi.")

def main(args=None):
    rclpy.init(args=args)
    node = PlantTaskManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
