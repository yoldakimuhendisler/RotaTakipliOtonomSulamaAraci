#!/bin/bash
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.
# Raspberry Pi 5 Sistemi Başlatma Betiği

echo "=== Otonom Araç Yönetim Sistemi (ROS2 & Backend) Başlatılıyor ==="

# Arkaplanda Yönetim Panelini ayağa kaldır
cd ../../backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

# ROS 2 Nodelarını ayağa kaldır
cd ../ros2_ws
source install/setup.bash
# Eger ortamda onceden ros sourcelandıysa sıkıntı cıkmaz (örn: /opt/ros/humble/setup.bash loginde sourcelandı varsayilir)
ros2 launch plant_bot robot_launch.py &
ROS_PID=$!

echo "Sistem Ayakta. Durdurmak için CTRL+C tuşlayın."
trap "echo 'Terminating...'; kill $BACKEND_PID $ROS_PID; exit 1" SIGINT SIGTERM
wait
