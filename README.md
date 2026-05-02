# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı 🌿

Bu kod bütünü **Aras Coşkun - [github.com/arascoskun0](https://github.com/arascoskun0)** tarafından oluşturulmuştur.

Bu proje **"Yoldaki Mühendisler"** takımı için otonom bir bitki sulama ağının kurulmasını sağlamak amacıyla geliştirilmiştir. Otonom kara aracı (Raspberry Pi 5 + ROS 2), Wi-Fi ağı üzerinden yapay zeka bilgisayarıyla *(AI Inference Server)* iletişim kurarak hareket eder, bitkileri tanır ve nem seviyelerine göre otonom olarak mekanik bir propla toprağı sulayıp sulamamaya karar verir. 

## 📁 Proje Klasör Yapısı (Monorepo)

- `/ai_server` : Görüntü işleme ve Bitki Tanıma görevini yapan FastAPI sunucusu. Bilgisayarda başlatılır ve port `9937` den hizmet verir.
- `/backend` : Web arayüzü ve telemetri verilerini kaydeden yönetim paneli (Araç durumu, loglar, sulama ölçümleri). Pi'nin kendi üstünde çalışır ve `8000` portundan paneli açar.
- `/ros2_ws` : Raspberry Pi'da kamera, motor, sensörler ve otonom karar ağacını (State Machine) yöneten ROS 2 paketi.
- `/deployment` : Takım arkadaşlarımızın bilgisayarlarında ve RPi'da sistemleri hızlıca kurmak ve koşturmak için hazırlanan `.bat` ve `.sh` scriptlerini barındırır.
- `/shared` : Ağlar ötesi veri yapısı iletişimi kuran ortak bileşenleri (Pydantic modelleri, ortam denetleyici vs.) içerir.

---

## 🔧 Donanım Kurulumu ve Pin Bağlantıları

Bu proje Raspberry Pi 5 üzerine kuruludur. Aşağıdaki sensör ve motor sürücülerin ilgili pinlere bağlanması gerekmektedir.

### Kullanılan Donanımların Listesi (Donanım BOM)
1. **Motor Sürcü:** L298N Motor Sürücü Kartı (Sağ ve sol DC tekerlek motorları için)
2. **Kamera:** Standart USB Web Kamerası veya Pi Camera Module 3
3. **Nem Sensörü:** Capacitive Soil Moisture Sensor v1.2 (Analog sensördür, dijital çevirici gereklidir)
4. **ADC Çevirici:** MCP3008 SPI ADC Entegresi (Nem sensörünü RPi'ye bağlamak için)
5. **Prob Mekanizması:** MG996R Servo Motor (Nem sensörünü mekanik olarak toprağa daldırıp çıkarmak için)
6. **Su Pompası:** 5V Dalgıç Su Pompası ve 1-Kanal 5V Röle Kartı (Suyu bitkiye aktarmak için)

### GPIO Pin Bağlantı Şeması (Raspberry Pi 5)

Sistemin bütünlüğünü korumak adına RPi 5 (Broadcom GPIO) pin konfigürasyonları aşağıdaki gibi tespit edilmiştir:

| Bileşen | RPi 5 Pin (BCM / GPIO) | RPi 5 Fiziksel Pin No | Açıklama |
|---|---|---|---|
| **L298N ENA (Sol Hız)** | GPIO 12 (PWM0) | Pin 32 | Sol motorların PWM hız kontrolü |
| **L298N IN1 & IN2** | GPIO 5, GPIO 6 | Pin 29, Pin 31 | Sol motor yönü (İleri/Geri) |
| **L298N IN3 & IN4** | GPIO 13, GPIO 19 | Pin 33, Pin 35 | Sağ motor yönü (İleri/Geri) |
| **L298N ENB (Sağ Hız)**| GPIO 18 (PWM1) | Pin 12 | Sağ motorların PWM hız kontrolü |
| **Servo (Prob İndir)** | GPIO 26 | Pin 37 | Probu aşağı/yukarı hareket ettiren servo sinyali |
| **Röle (Su Pompası)** | GPIO 21 | Pin 40 | Su pompasını tetikleyen High/Low pini |

#### MCP3008 (Analog/Dijital Dönüştürücü) Toprak Sensörü Bağlantıları
Kapasitif sensör analog voltaj okuması verdiğinden, SPI üzerinden MCP3008'e bağlanmıştır.

| MCP3008 Pin | RPi 5 Pin / Diğer Yön |
|---|---|
| VDD & VREF | RPi 3.3V (Örn: Pin 1) |
| AGND & DGND | RPi GND (Ortak Toprak, Örn: Pin 6) |
| CLK | GPIO 11 (Pin 23) (SCLK) |
| DOUT | GPIO 9 (Pin 21) (MISO) |
| DIN | GPIO 10 (Pin 19) (MOSI) |
| CS/SHDN | GPIO 8 (Pin 24) (CE0) |
| CH0 | Nem Sensörü Analog Veri Kablosu (AOUT) |

*Not: Nem sensörünün VCC'si 3.3V'a ve GND'si ortak GND'ye bağlanmalıdır.*

### 🛠️ Sensör ve Mekanik Kurulum Adımları
1. L298N motor sürücüye bataryalarınızdan (örn. 11.1V LiPo veya 12V pil bloğu) direkt güç verin, 5V dönüşümünü açın ve L298N GND eksenini RPi'nin GND ekseniyle **mutlaka birleştirin**.
2. Sağ ve sol motorların artı eksi kutuplarını L298N çıkışlarına bağlayın. ENA, ENB, IN1, IN2, IN3, IN4 pinlerini RPi'ye tabloda yazdığı şekilde jumper kablolar ile girin.
3. Servo motor ve Röleyi RPi dışındaki harici bir 5V kaynağından (regülatör) beslemeniz önerilir (RPi 5 akımı yetmeyebilir). Sadece sinyal (Data/PWM) kablolarını (GPIO 26 ve GPIO 21) RPi'ye takın.
4. MCP3008 entegresini breadboard'a saplayın ve tüm SPI jumperlarını (MOSI, MISO, SCLK, CE0) Raspberry Pi üzerine takın.
5. Capacitive Soil Moisture Sensor'ı MG996R Servonun koluna yapııştırın veya plastik cırtla bağlayın, sensör ucunu aşağı sarkıtın. Data ucunu breadboarda CH0'a girin. Pompaya su borusunu bağlayın ve ucunu robotun ön kısmından toprağa yönlendirin.
6. Kamerayı RPi'nin USB portlarından birine takarak öne bakacak şekilde araca sabitleyin.

---

## 🚀 Yazılım Kurulumu ve Çalıştırma (Takım İçin Rehber)

Proje iki donanım cihazı arasında bölüştürülmüş durumdadır: **1. AI Sunucusu (Geliştirici PC'si)** ve **2. Raspberry Pi 5 (Araç Kontrolcüsü).** Donanımların entegrasyonlarını test ederken `.sim_mode` kullanarak araba üzerinde hiçbir elektronik takılı olmadan kodları test etme / geliştirme lüksüne sahibiz.

### 1) AI Sunucusunu (Bilgisayarınızı) Ayağa Kaldırma
Bilgisayarınızı (Windows veya Ubuntu) Raspberry Pi aracının oluşturduğu `RotaTakipliOtonomSulamaAraci` isimli ağa bağlayın (Şifre: `MuhendisAdam29`). Sistem cihazınıza IP olarak `192.168.50.2` verecek. Böylece AI sunucunuz `192.168.50.2:9937` adresinde çalışıyor olacak ve robot kendi içindeki kodlarla sizi direkt bulabilecek.

**Windows Cihazlar için Kurulum/Başlatma:**
1. `deployment\pc\setup_pc.bat` çalıştırarak Python bağımlılıklarını kurun. (Bu sadece 1 kez yapılır)
2. `deployment\pc\start_pc.bat` tıklayarak AI sunucunuzu ayağa kaldırın.

**Ubuntu / Linux Cihazlar için Kurulum/Başlatma:**
1. `cd deployment/pc`
2. `chmod +x setup_pc.sh && ./setup_pc.sh`
3. `chmod +x start_pc.sh && ./start_pc.sh`

### 2) Ana Arabamızı (Raspberry Pi 5) Ayağa Kaldırma
Ahududu Pi (`Raspberry Pi 5`) üzerinde de internet erişimi olan bir ana terminal açın. Pi, ortamda kendisini bir verici anten (Hotspot) olarak ayarlayıp kodları derleyecek.

**Pi'da (Linux Terminalinde):**
1. `cd deployment/rpi`
2. `chmod +x setup_rpi.sh && ./setup_rpi.sh`
   -  *(Not: Kurulum sürecinde Wi-Fi ayarlarınız değişebilir, Pi lokal Hotspot moduna geçer.)*
3. `chmod +x start_rpi.sh && ./start_rpi.sh`
4. Araba artık 192.168.50.1 sunucusu üstünden çalışıyor olarak log atmaya başlayacaktır.

> *Yönetim Paneline Erişmek İçin Pi aği içindeyken tarayıcıdan `http://192.168.50.1:8000` adresine gidebilirsiniz.*

---

## 🛠️ Simülasyon Modunda Donanımsız Test Etme (`.sim_mode`)
Henüz su motorları (pompalar), motor sürücü mekanlikleri veya RealSense kamera arabaya fiziksel olarak takılı değilse de sistemin ROS nodelarını sorunsuzca koşturmak mümkündür:  
Bunun için ana dizinde (bu klasörde) boş bir `.sim_mode` dosyası oluşturmalısınız (Veya `make sim` yazabilirsiniz).

Böylece Mock Nodelar devreye girecek; hayali olarak sahte bir nem ölçecek, sahte bir derinlik haritası verecek, tekerlekler dönüyormuş gibi davranıp ROS ağında state machine'i sulama yapıp hedef aramaya sevk edecektir ve bunları size Log panelinizde/Backend'de gösterecektir. Eğer `.sim_mode` yokken scriptleri donanımsız ayağa kaldırmaya çalışırsanız (RPi.GPIO benzeri kodlar yükleneceğinden) muhtemelen çökecektir.
