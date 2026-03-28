# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import os
import subprocess
import sys

def run_cmd(cmd):
    print(f"Executing: {cmd}")
    subprocess.call(cmd, shell=True)

def main():
    print("=== Raspberry Pi 5 AP ve Bağımlılık Kurulumu ===")
    
    # 1. Kutuphaneleri Kur
    print("1. Backend gereksinimleri Python ortamına indiriliyor...")
    req_path = os.path.join("..", "..", "backend", "requirements.txt")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
    
    # 2. ROS Paketlerini Derle
    print("2. ROS 2 paketi derleniyor...")
    run_cmd("cd ../../ros2_ws && colcon build --symlink-install")
    
    # 3. Access Point Olustur
    print("3. Wi-Fi Access Point (SSID: RotaTakipliOtonomSulamaAraci) Ayarları (Sudo yetkisi isteyecektir)...")
    run_cmd('sudo nmcli con add type wifi ifname wlan0 mode ap con-name RotaTakipliOtonomSulamaAraci ssid RotaTakipliOtonomSulamaAraci ipv4.method shared ipv4.addresses 192.168.50.1/24 wifi-sec.key-mgmt wpa-psk wifi-sec.psk "MuhendisAdam29" || true')
    run_cmd('sudo nmcli con up RotaTakipliOtonomSulamaAraci')
    
    # 4. Sadece ilk baglanan cihaza (AI Server) statik IP (192.168.50.2) atanmasini garantile
    print("4. DHCP kilitleniyor (AI Server'in mecburen statik IP alması için)...")
    run_cmd('sudo mkdir -p /etc/NetworkManager/dnsmasq-shared.d/')
    run_cmd('echo "dhcp-range=192.168.50.2,192.168.50.2,12h" | sudo tee /etc/NetworkManager/dnsmasq-shared.d/custom-dhcp.conf')
    run_cmd('sudo systemctl restart NetworkManager')

    print("=== Kurulum Basariyla Tamamlandi ===")

if __name__ == "__main__":
    main()
