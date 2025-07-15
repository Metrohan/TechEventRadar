#!/bin/bash

echo "Python3 kontrol ediliyor..."
if ! command -v python3 &> /dev/null
then
    echo "Hata: Python3 bulunamadi. Lutfen Python3'u yukleyin."
    echo "Kurulum bilgisi icin: https://www.python.org/downloads/"
    exit 1
fi
echo "Python3 bulundu."

echo "Google Chrome/Chromium tarayici kontrol ediliyor..."
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null
then
    echo "Hata: Google Chrome veya Chromium tarayicisi bulunamadi."
    echo "Lutfen tarayicinizi yukleyin (orn: sudo apt install chromium-browser veya Google Chrome resmi sitesinden indirin)."
    echo "Chrome: https://www.google.com/chrome/"
    exit 1
fi
echo "Google Chrome/Chromium bulundu."

echo "Bagimliliklar yukleniyor..."
pip install -r requirements.txt

echo "Scraper calistiriliyor..."
python3 app.py

echo "Islem tamamlandi."