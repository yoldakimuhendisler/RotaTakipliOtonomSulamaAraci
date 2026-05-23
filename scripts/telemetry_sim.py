# Yoldaki Mühendisler - Telemetri ve Log Simülatörü
# ROS 2 ve donanım bağımlılığı olmadan web arayüzünü test etmek için yazılmıştır.

import time
import math
import random
import requests

BACKEND_URL = "http://127.0.0.1:8000"
TELEMETRY_ENDPOINT = f"{BACKEND_URL}/api/telemetry"
PLANTS_ENDPOINT = f"{BACKEND_URL}/api/plants"
LOGS_ENDPOINT = f"{BACKEND_URL}/api/logs"

PLANT_SPECIES = ["Domates", "Biber", "Salatalık", "Çilek", "Nane", "Reyhan"]

def post_log(level, module, message):
    try:
        requests.post(LOGS_ENDPOINT, json={
            "level": level,
            "module": module,
            "message": message
        }, timeout=1.0)
    except Exception as e:
        print(f"Log gönderilemedi: {e}")

def post_telemetry(x, y, battery, water, state):
    try:
        requests.post(TELEMETRY_ENDPOINT, json={
            "robot_x": float(x),
            "robot_y": float(y),
            "battery_level": float(battery),
            "water_level": float(water),
            "current_state": str(state),
            "is_sim_mode": True
        }, timeout=1.0)
    except Exception as e:
        print(f"Telemetri gönderilemedi: {e}")

def post_new_plant(x, y, species):
    try:
        res = requests.post(PLANTS_ENDPOINT, json={
            "location_x": float(x),
            "location_y": float(y),
            "species": str(species)
        }, timeout=1.0)
        return res.json()
    except Exception as e:
        print(f"Bitki kaydedilemedi: {e}")
        return None

def run_simulation():
    print("=== Otonom Sulama Aracı Simülasyonu Başlatıldı ===")
    print("Veriler localhost:8000 üzerindeki backend sunucusuna aktarılacak.")
    
    # Başlangıç durumu
    battery = 100.0
    water = 100.0
    state = "BAŞLATILIYOR"
    t = 0.0
    
    # Başlangıç logları
    time.sleep(2)
    post_log("INFO", "Sistem", "Otonom araç simülasyon modunda ayağa kalktı.")
    post_log("INFO", "Ağ", "FastAPI Sunucusu ile websocket kanalı kuruldu.")
    post_log("INFO", "Donanım", "MCP3008 ADC SPI arabirimi simüle ediliyor.")
    post_log("INFO", "Kamera", "USB Web Kamerası mock yayını aktif.")
    
    state = "ARAMA (Lissajous Rota Takibi)"
    post_log("INFO", "Navigasyon", "Otonom arama rotası başlatıldı. Hedef taranıyor...")
    
    plant_detection_cooldown = 0
    
    while True:
        # 1. Koordinat Güncelleme (Lissajous Eğrisi / Sonsuzluk işareti şeklinde hareket)
        # x = 3.5 * sin(t), y = 2.5 * sin(2t) -> -3.5 ile +3.5 aralığında gezinir
        x = 3.2 * math.sin(t * 0.15)
        y = 2.2 * math.sin(t * 0.3)
        
        # 2. Batarya ve Su Eksilmesi
        battery -= 0.15
        water -= 0.05
        
        # Sınır kontrolleri ve şarj/su doldurma simülasyonu
        if battery <= 20.0 and battery > 19.7:
            post_log("WARNING", "Güç", "Batarya seviyesi düşük! (%20)")
        elif battery <= 5.0 and battery > 4.7:
            post_log("ERROR", "Güç", "Kritik Güç! Batarya seviyesi %5'in altında.")
        elif battery <= 0:
            post_log("INFO", "Sistem", "Batarya tükendi. Otomatik şarj istasyonuna yönleniliyor...")
            time.sleep(2)
            battery = 100.0
            post_log("INFO", "Sistem", "Şarj tamamlandı. Göreve geri dönülüyor.")
            
        if water <= 10.0 and water > 9.7:
            post_log("WARNING", "Su Deposu", "Su tankı seviyesi kritik seviyede! (%10)")
        elif water <= 0:
            post_log("INFO", "Sistem", "Su deposu tükendi. Su dolum istasyonuna dönülüyor...")
            time.sleep(2)
            water = 100.0
            post_log("INFO", "Sistem", "Su tankı tamamen dolduruldu.")
            
        # 3. Rastgele Bitki Keşfi (Cooldown kontrolüyle her 20-30 saniyede bir)
        plant_detection_cooldown += 1
        if plant_detection_cooldown > 15 and random.random() < 0.12:
            state = "BİTKİ ALGILANDI"
            post_telemetry(x, y, battery, water, state)
            
            species = random.choice(PLANT_SPECIES)
            post_log("INFO", "Yapay Zeka", f"YoloV8: Ön kamerada {species} bitkisi algılandı! (X: {x:.2f}, Y: {y:.2f})")
            time.sleep(1.5)
            
            state = "PROB DALIŞI"
            post_telemetry(x, y, battery, water, state)
            post_log("INFO", "Servo", "MG996R motor tetiklendi: Toprak nem sensörü probu toprağa indiriliyor...")
            time.sleep(2)
            
            # Sahte nem okuma
            moisture = random.randint(15, 65)
            post_log("INFO", "Sensör", f"MCP3008 ADC CH0: Toprak nem oranı %{moisture} olarak ölçüldü.")
            
            if moisture < 40:
                state = "SULAMA AKTİF"
                post_telemetry(x, y, battery, water, state)
                post_log("WARNING", "Karar Ağacı", f"Nem oranı eşik değerin (%40) altında! Sulama kararı alındı.")
                post_log("INFO", "Pompa", "5V Röle tetiklendi, su pompası çalışıyor...")
                time.sleep(3)
                
                water_used = random.randint(10, 20)
                water = max(0.0, water - water_used)
                post_log("INFO", "Pompa", f"Sulama tamamlandı. {water_used * 10}ml su toprağa verildi.")
                
                # Bitkiyi veritabanına kaydet
                post_new_plant(x, y, species)
                post_log("INFO", "Veritabanı", f"Sulanan {species} bitkisi koordinatlarıyla lokal veritabanına kaydedildi.")
            else:
                post_log("INFO", "Karar Ağacı", "Toprak nemi yeterli, sulamaya ihtiyaç duyulmadı.")
            
            state = "PROB YUKARI"
            post_telemetry(x, y, battery, water, state)
            post_log("INFO", "Servo", "Sensör probu geri çekildi.")
            time.sleep(1.5)
            
            # Arama durumuna geri dön
            state = "ARAMA (Lissajous Rota Takibi)"
            plant_detection_cooldown = 0
            
        # Telemetriyi gönder
        post_telemetry(x, y, battery, water, state)
        
        # Döngü zamanlaması
        t += 0.5
        time.sleep(1.0)

if __name__ == "__main__":
    # Backend sunucusunun başlaması için biraz bekle
    time.sleep(2)
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\nSimülasyon durduruldu.")
