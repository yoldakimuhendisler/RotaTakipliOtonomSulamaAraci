.PHONY: help sim run-ai run-backend build-ros run-ros 

help:
	@echo "Otonom Bitki Sulama Aracı Kurulum ve Çalıstırma Komutları"
	@echo "  make sim        : Projeyi simülasyon (.sim_mode) moduna geçirir"
	@echo "  make run-ai     : Ayrı bir terminalde AI sunucusunu port 9937'de başlatır"
	@echo "  make run-backend: Web arayüzü ve API'yi port 8000'de başlatır"
	@echo "  make build-ros  : ROS 2 paketini derler"
	@echo "  make run-ros    : Derlenmiş ROS 2 arabasını (tüm nodelarıyla) baslatır"

sim:
	touch .sim_mode
	@echo "Simülasyon Modu Aktif. (.sim_mode dosyasi olustu. Donanim aranmayacak.)"

run-ai:
	cd ai_server && uvicorn main:app --host 0.0.0.0 --port 9937 --reload

run-backend:
	cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

build-ros:
	cd ros2_ws && colcon build --symlink-install

run-ros:
	@echo "ROS 2 başlatılıyor... (Sisteminize baglı olarak 'source /opt/ros/humble/setup.bash' ve 'source ros2_ws/install/setup.bash' yapmis olmaniz gerekir)"
	cd ros2_ws && ros2 launch plant_bot robot_launch.py
