# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import Header

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from shared.utils.env_checker import is_sim_mode

class MappingNode(Node):
    def __init__(self):
        super().__init__('mapping_node')
        self.publisher_ = self.create_publisher(OccupancyGrid, 'map', 10)
        self.timer = self.create_timer(5.0, self.timer_callback)
        self.sim_mode = is_sim_mode()
        self.get_logger().info("Mapping Node baslatildi (2.5D Traversability Grid).")

    def timer_callback(self):
        # Dummy map yayını. Eger donanim varsa derinlik kamerasindan donusturulur.
        grid = OccupancyGrid()
        grid.header = Header(stamp=self.get_clock().now().to_msg(), frame_id="map")
        grid.info.resolution = 0.05
        grid.info.width = 100
        grid.info.height = 100
        
        # Basit bir 100x100 bos harita (hepsi 0 - gecilebilir)
        data = [0] * (100 * 100)
        grid.data = data
        self.publisher_.publish(grid)

def main(args=None):
    rclpy.init(args=args)
    node = MappingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
