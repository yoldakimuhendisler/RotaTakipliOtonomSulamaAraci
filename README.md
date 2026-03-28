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

## 🚀 Çalıştırma ve Kurulum (Takım İçin Rehber)

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
