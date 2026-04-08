#!/usr/bin/env python3
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from shared.utils.env_checker import is_sim_mode
from shared.utils.logger import get_logger

logger = get_logger("HardwareWrapper")

class SoilProbePlatform:
    def __init__(self):
        self.sim_mode = is_sim_mode()
        if not self.sim_mode:
            logger.info("Donanım Modu Aktif: Toprak Nem Probu başlatıldı.")
        else:
            logger.info("Simülasyon Modu Aktif: Toprak Nem Probu mocklandı.")
            
    def probe_down(self):
        if self.sim_mode:
            logger.info("[SIM] Prob mekanizması aşağı indiriliyor...")
        else:
            pass # RPi.GPIO vb kütüphanelerle servo/motor sür
            
    def probe_up(self):
        if self.sim_mode:
            logger.info("[SIM] Prob mekanizması yukarı çekiliyor...")
        else:
            pass # RPi.GPIO

    def read_moisture(self) -> float:
        if self.sim_mode:
            import random
            val = round(random.uniform(20.0, 80.0), 2)
            logger.info(f"[SIM] Nem okundu: {val}%")
            return val
        else:
            # Gerçek ADC veya SPI okuması
            return 0.0 

class WaterPump:
    def __init__(self):
        self.sim_mode = is_sim_mode()
        if not self.sim_mode:
             logger.info("Donanım Modu Aktif: Su pompası başlatıldı.")
        else:
             logger.info("Simülasyon Modu Aktif: Su pompası mocklandı.")

    def run_pump(self, duration_sec: float):
        if self.sim_mode:
            logger.info(f"[SIM] Su pompası {duration_sec} saniye çalıştırıldı.")
        else:
            pass # GPIO HIGH, wait, GPIO LOW
