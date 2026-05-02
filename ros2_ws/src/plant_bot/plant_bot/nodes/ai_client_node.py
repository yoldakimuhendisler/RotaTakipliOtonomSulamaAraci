#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

import os
import requests
import json
import cv2
import numpy as np

try:
    from cv_bridge import CvBridge
except ImportError:
    CvBridge = None

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
        
        # IP config okuma (README'ye gore PC'nin alacagi statik IP 192.168.50.2)
        self.ai_host = os.environ.get("AI_SERVER_HOST", "192.168.50.2")
        self.ai_port = os.environ.get("AI_SERVER_PORT", "9937")
        self.ai_url = f"http://{self.ai_host}:{self.ai_port}/infer"
        
        if CvBridge is not None:
            self.br = CvBridge()
        else:
            self.br = None
        
        self.get_logger().info(f"AI Client Node başlatıldı. Hedef: {self.ai_url}")
        
    def listener_callback(self, msg: Image):
        try:
            image_data = b'dummy_image_data_from_ros'
            if self.br is not None:
                try:
                    # Gelen ROS Image mesajini BGR formatinda OpenCV imajina donustur
                    cv_image = self.br.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                    # JPEG olarak encode et
                    _, encoded_img = cv2.imencode('.jpg', cv_image)
                    image_data = encoded_img.tobytes()
                except Exception as e:
                    self.get_logger().error(f"Goruntu donusturme hatasi: {e}")
            
            files = {'file': ('frame.jpg', image_data, 'image/jpeg')}
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
