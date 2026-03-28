# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path

class RoutePlannerNode(Node):
    def __init__(self):
        super().__init__('route_planner_node')
        self.subscription = self.create_subscription(PoseStamped, 'goal_pose', self.goal_callback, 10)
        self.publisher_ = self.create_publisher(Path, 'plan', 10)
        self.get_logger().info("A* tabanli Route Planner Node baslatildi.")

    def goal_callback(self, msg: PoseStamped):
        # A* varsayilip direkt duz cizgi plani donulur (Mock / Prototip)
        self.get_logger().info(f"Yeni hedef alindi: x={msg.pose.position.x}, y={msg.pose.position.y}")
        path_msg = Path()
        path_msg.header = msg.header
        
        # Baslangic noktasi
        start_pose = PoseStamped()
        start_pose.pose.position.x = 0.0
        start_pose.pose.position.y = 0.0
        
        path_msg.poses = [start_pose, msg] # Duz cizgi
        self.publisher_.publish(path_msg)

def main(args=None):
    rclpy.init(args=args)
    node = RoutePlannerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
