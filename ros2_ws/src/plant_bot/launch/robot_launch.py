#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import launch
import launch_ros.actions

def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='plant_bot',
            executable='camera_node',
            name='camera_node'),
        launch_ros.actions.Node(
            package='plant_bot',
            executable='mapping_node',
            name='mapping_node'),
        launch_ros.actions.Node(
            package='plant_bot',
            executable='ai_client_node',
            name='ai_client_node'),
        launch_ros.actions.Node(
            package='plant_bot',
            executable='plant_task_manager',
            name='plant_task_manager',
            output='screen'), # Konsola detaylı log bassın
        launch_ros.actions.Node(
            package='plant_bot',
            executable='motion_control_node',
            name='motion_control_node'),
        launch_ros.actions.Node(
            package='plant_bot',
            executable='soil_probe_node',
            name='soil_probe_node'),
        launch_ros.actions.Node(
            package='plant_bot',
            executable='watering_node',
            name='watering_node'),
        launch_ros.actions.Node(
            package='plant_bot',
            executable='water_level_node',
            name='water_level_node'),
        launch_ros.actions.Node(
            package='plant_bot',
            executable='backend_bridge_node',
            name='backend_bridge_node'),
  ])
