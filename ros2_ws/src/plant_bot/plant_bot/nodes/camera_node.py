# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from shared.utils.env_checker import is_sim_mode

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        self.publisher_ = self.create_publisher(Image, 'camera/rgb', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.sim_mode = is_sim_mode()
        
        if self.sim_mode:
            self.get_logger().info("SIM MODU: Sahte RGB kamera verisi yayinlanacak.")
        else:
            self.get_logger().info("GERCEK MOD: Intel RealSense baslatilacak (Mock eglendiginde acilir).")

    def timer_callback(self):
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.height, msg.width = 480, 640
        msg.encoding = 'rgb8'
        
        if self.sim_mode:
            # Sadece yesilimsi bir test formati
            fake_img = np.zeros((480, 640, 3), dtype=np.uint8)
            fake_img[:, :, 1] = 150
            msg.step = 640 * 3
            msg.data = fake_img.tobytes()
        else:
            # Gercek rs.pipeline read vs.
            msg.data = b'' 

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
