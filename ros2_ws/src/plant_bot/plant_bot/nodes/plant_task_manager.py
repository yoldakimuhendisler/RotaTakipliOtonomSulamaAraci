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
        self.state_start_time = time.time()
        self.subscription_ai = self.create_subscription(String, 'ai/detections', self.ai_callback, 10)
        
        self.probe_cmd_pub = self.create_publisher(String, 'soil_probe/command', 10)
        self.water_cmd_pub = self.create_publisher(Float32, 'watering/command_duration', 10)
        self.probe_res_sub = self.create_subscription(Float32, 'soil_probe/moisture', self.moisture_callback, 10)
        
        self.timer = self.create_timer(1.0, self.state_machine_loop)
        self.get_logger().info("Görev Yöneticisi (State Machine) başlatıldı. Durum: SEARCHING")
        self.target_found = False
        self.moisture_val = None

    def change_state(self, new_state):
        self.state = new_state
        self.state_start_time = time.time()

    def ai_callback(self, msg: String):
        try:
            if self.state == "SEARCHING":
                if "Plant" in msg.data and "success\": true" in msg.data.lower():
                    self.target_found = True
                    self.get_logger().info("Bitki tespit edildi! Durum: APPROACHING")
                    self.change_state("APPROACHING")
        except Exception as e:
            self.get_logger().error(f"AI Callback hatasi: {e}")

    def moisture_callback(self, msg: Float32):
        try:
            if self.state == "MEASURING":
                self.moisture_val = msg.data
                self.get_logger().info(f"Nem okundu: {self.moisture_val}%")
                if self.moisture_val < 40.0:
                    self.get_logger().info("Nem yetersiz (<%40), sulama yapilacak.")
                    self.change_state("WATERING")
                    
                    # Sulama komutunu gonder
                    msg_water = Float32()
                    msg_water.data = 3.0 # 3 saniye sula
                    self.water_cmd_pub.publish(msg_water)
                else:
                    self.get_logger().info("Nem yeterli, sulama yapilmayacak. Sonraki hedefe geciliyor.")
                    self.target_found = False
                    self.change_state("SEARCHING")
        except Exception as e:
            self.get_logger().error(f"Nem Callback hatasi: {e}")

    def state_machine_loop(self):
        try:
            current_time = time.time()
            elapsed = current_time - self.state_start_time

            if self.state == "APPROACHING":
                if elapsed < 2.0:
                    # Sadece bir kere yazdir
                    if elapsed < 1.0:
                        self.get_logger().info("Hedefe yaklaşılıyor...")
                else:
                    self.change_state("MEASURING")
                    self.get_logger().info("Nem ölçme komutu gönderiliyor.")
                    msg = String()
                    msg.data = "MEASURE"
                    self.probe_cmd_pub.publish(msg)
                
            elif self.state == "WATERING":
                if elapsed > 5.0:
                    self.target_found = False
                    self.get_logger().info("Sulama bitti. Tekrar arayisa cikildi.")
                    self.change_state("SEARCHING")
                    
        except Exception as e:
            self.get_logger().error(f"State Machine hatasi: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = PlantTaskManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
