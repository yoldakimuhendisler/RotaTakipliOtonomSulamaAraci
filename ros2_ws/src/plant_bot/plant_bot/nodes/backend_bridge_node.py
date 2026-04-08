#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
import requests
import json

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
    
from shared.models.common import TelemetryData
from shared.utils.env_checker import is_sim_mode

class BackendBridgeNode(Node):
    def __init__(self):
        super().__init__('backend_bridge_node')
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.backend_url = "http://127.0.0.1:8000/api/telemetry"
        self.sim_mode = is_sim_mode()
        self.get_logger().info("Backend Bridge Node baslatildi. Telemetri verisi Web'e aktarilacak.")

    def timer_callback(self):
        data = TelemetryData(
            robot_x=0.0,
            robot_y=0.0,
            battery_level=100.0,
            water_level=5.0,
            current_state="SEARCHING (Mock)",
            is_sim_mode=self.sim_mode
        )
        try:
            requests.post(self.backend_url, json=data.dict(), timeout=1.0)
        except Exception:
            self.get_logger().warn("Backend sunucusuna erisilemedi. (http://localhost:8000 calisiyor mu?)")

def main(args=None):
    rclpy.init(args=args)
    node = BackendBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
