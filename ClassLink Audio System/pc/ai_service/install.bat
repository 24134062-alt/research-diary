@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║          ClassLink AI Service - Cài Đặt                          ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Chưa cài Python! Vui lòng cài Python 3.10+ từ python.org
    pause
    exit /b 1
)

echo ✅ Tìm thấy Python
echo.

:: Create venv
echo [1/5] Tạo môi trường ảo...
if not exist "venv" (
    python -m venv venv
)

:: Activate venv
echo [2/5] Kích hoạt môi trường ảo...
call venv\Scripts\activate.bat

:: Install deps
echo [3/5] Cài đặt thư viện...
pip install -r requirements.txt --quiet

:: Setup config
echo [4/5] Cấu hình API Key...
if not exist "config.env" (
    copy .env.example config.env >nul
    echo.
    echo ⚠️  Đã tạo file config.env
    echo     Vui lòng mở file và thêm GEMINI_API_KEY của bạn!
    echo.
    echo     Lấy API Key miễn phí tại:
    echo     https://aistudio.google.com/app/apikey
    echo.
    notepad config.env
)

:: Add to Windows Startup
echo [5/5] Cài đặt tự động khởi động...
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "CURRENT_DIR=%~dp0"

:: Create VBS script for silent start
echo Set WshShell = CreateObject("WScript.Shell") > "%CURRENT_DIR%start_silent.vbs"
echo WshShell.CurrentDirectory = "%CURRENT_DIR%" >> "%CURRENT_DIR%start_silent.vbs"
echo WshShell.Run chr(34) ^& "%CURRENT_DIR%start.bat" ^& chr(34), 0 >> "%CURRENT_DIR%start_silent.vbs"

:: Create shortcut in Startup folder
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%STARTUP_FOLDER%\ClassLink AI Service.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%CURRENT_DIR%start_silent.vbs" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "ClassLink AI Service Auto Start" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  ✅ Cài đặt hoàn tất!                                            ║
echo ║                                                                   ║
echo ║  🚀 AI Service sẽ TỰ ĐỘNG CHẠY khi bật máy!                      ║
echo ║                                                                   ║
echo ║  📝 Tiếp theo:                                                   ║
echo ║  1. Kiểm tra GEMINI_API_KEY trong config.env                    ║
echo ║  2. Chạy start.bat lần đầu để test                              ║
echo ║  3. Những lần sau chỉ cần mở web dashboard!                     ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
pause
