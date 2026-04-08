#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    pkg_plant_bot = get_package_share_directory('plant_bot')
    world_path = os.path.join(pkg_plant_bot, 'worlds', 'farm.world')
    urdf_path = os.path.join(pkg_plant_bot, 'urdf', 'plant_bot.urdf')

    # Start Gazebo Server and Client with the given world
    gazebo_server = ExecuteProcess(
        cmd=['gzserver', '--verbose', world_path, '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )

    gazebo_client = ExecuteProcess(
        cmd=['gzclient'],
        output='screen'
    )

    # Robot State Publisher Node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': open(urdf_path).read()}]
    )

    # Spawn entity
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'plant_bot', '-file', urdf_path, '-x', '0.0', '-y', '0.0', '-z', '0.3'],
        output='screen'
    )

    return LaunchDescription([
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        spawn_entity
    ])
