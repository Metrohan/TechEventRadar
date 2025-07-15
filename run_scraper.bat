@echo off
REM Bu dosya gerekli önkoşulları yükler ve TechEventRadar'ı hızlıca başlatır

REM Python'ın yüklü olduğundan emin olun
where python >nul 2>nul
if %errorlevel% neq 0 (
	echo Python bulunamadi. Lutfen Python'i yukleyin ve PATH'inize ekleyin.
	echo https://www.python.org/downloads/
	pause
	exit /b 1
)

REM Google Chrome'un tam yolunu belirtin.
REM Genellikle C:\Program Files\Google\Chrome\Application\chrome.exe konumunda bulunur.
REM Eger burada bulamazsa ve 64-bit bir sistemdeyseniz (x86) klasorunu de kontrol edebilirsiniz.
set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"

REM Chrome'un varligini kontrol et
if not exist "%CHROME_PATH%" (
    echo Google Chrome belirtilen yolda bulunamadi: "%CHROME_PATH%"
    echo Lutfen Chrome'un yuklu oldugundan ve yukaridaki yolun dogru oldugundan emin olun.
    echo Gerekirse, "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" yolunu deneyebilirsiniz.
    echo https://www.google.com/chrome/
    pause
    exit /b 1
)

REM Gerekli Python kütüphanelerini yükle
echo Bagimliliklar yukleniyor
pip install -r requirements.txt

REM Scraper'i calistir
echo Scraper calistiriliyor
python app.py

echo Islem tamamlandi.
pause