#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

from setuptools import setup
import os
from glob import glob

package_name = 'plant_bot'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name, f'{package_name}.nodes', f'{package_name}.core', f'{package_name}.hardware'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ],
    install_requires=['setuptools', 'rclpy', 'requests'],
    zip_safe=True,
    maintainer='Aras',
    maintainer_email='aras@example.com',
    description='Otonom Bitki Sulama Aracı ROS 2 Paketi',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_node = plant_bot.nodes.camera_node:main',
            'mapping_node = plant_bot.nodes.mapping_node:main',
            'route_planner_node = plant_bot.nodes.route_planner_node:main',
            'ai_client_node = plant_bot.nodes.ai_client_node:main',
            'plant_task_manager = plant_bot.nodes.plant_task_manager:main',
            'motion_control_node = plant_bot.nodes.motion_control_node:main',
            'soil_probe_node = plant_bot.nodes.soil_probe_node:main',
            'watering_node = plant_bot.nodes.watering_node:main',
            'water_level_node = plant_bot.nodes.water_level_node:main',
            'backend_bridge_node = plant_bot.nodes.backend_bridge_node:main'
        ],
    },
)
