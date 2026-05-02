#!/bin/bash
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.
# RaspberryPi 5 Kurulum Batici
echo "Kurulum Basliyor..."
cd deployment/rpi
chmod +x setup_rpi.py
python3 setup_rpi.py
echo "Bitti!"
