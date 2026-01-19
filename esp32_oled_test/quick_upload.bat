@echo off
echo ==========================================
echo ESP32 QUICK UPLOAD - Text chay dai
echo ==========================================
echo.
echo Huong dan:
echo 1. RUT day USB ESP32 ra
echo 2. Nhan phim bat ky de tiep tuc...
pause
echo.
echo 3. CAM LAI day USB ESP32
echo 4. Cho 3 giay...
timeout /t 3
echo.
echo Uploading...
cd /d "%~dp0"
pio run --target upload
echo.
echo ==========================================
if errorlevel 1 (
    echo THAT BAI! Thu lai:
    echo - Kiem tra day USB
    echo - Dong tat ca Serial Monitor
    echo - Chay lai file nay
) else (
    echo THANH CONG!
    echo ESP32 dang hien thi chu chay!
)
echo ==========================================
pause
