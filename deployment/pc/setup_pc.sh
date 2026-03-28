#!/bin/bash
# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.
# Bilgisayar Kurulum Batici (Ubuntu/Linux)

echo "=== AI Sunucusu Ubuntu/Linux Kurulumu ==="
cd ../../ai_server

# Gerekli bagimliliklari kurar
pip3 install -r requirements.txt

echo "=== Kurulum Bitti. Saf Python bilesenleri kuruldu. ./start_pc.sh ile baslatabilirsiniz ==="
