# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

import os
import requests
import json

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

class AIClientNode(Node):
    def __init__(self):
        super().__init__('ai_client_node')
        self.subscription = self.create_subscription(
            Image,
            'camera/rgb',
            self.listener_callback,
            10
        )
        self.publisher_ = self.create_publisher(String, 'ai/detections', 10)
        
        # IP config okuma
        self.ai_host = os.environ.get("AI_SERVER_HOST", "127.0.0.1")
        self.ai_port = os.environ.get("AI_SERVER_PORT", "9937")
        self.ai_url = f"http://{self.ai_host}:{self.ai_port}/infer"
        
        self.get_logger().info(f"AI Client Node başlatıldı. Hedef: {self.ai_url}")
        
    def listener_callback(self, msg: Image):
        # Gercek senaryoda cv2.imencode('.jpg', img)[1].tobytes()
        try:
            files = {'file': ('frame.jpg', b'dummy_image_data_from_ros', 'image/jpeg')}
            response = requests.post(self.ai_url, files=files, timeout=2.0)
            
            if response.status_code == 200:
                result = response.text
                pub_msg = String()
                pub_msg.data = result
                self.publisher_.publish(pub_msg)
            else:
                self.get_logger().warn(f"AI Servis hatasi: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.get_logger().error(f"AI Servisine erisilemedi. Baglanti Hatasi.")

def main(args=None):
    rclpy.init(args=args)
    node = AIClientNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
