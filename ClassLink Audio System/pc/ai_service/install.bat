@echo off
echo.
echo ==================================================================
echo          ClassLink AI Service - Cai Dat
echo ==================================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Chua cai Python! Vui long cai Python 3.10+ tu python.org
    pause
    exit /b 1
)

echo [OK] Tim thay Python
echo.

:: Create venv
echo [1/5] Tao moi truong ao...
if not exist "venv" (
    python -m venv venv
)

:: Activate venv
echo [2/5] Kich hoat moi truong ao...
call venv\Scripts\activate.bat

:: Install deps
echo [3/5] Cai dat thu vien...
pip install -r requirements.txt --quiet

:: Setup config
echo [4/5] Cau hinh API Key...
if not exist "config.env" (
    copy .env.example config.env >nul
    echo.
    echo [!] Da tao file config.env
    echo     Vui long mo file va them GEMINI_API_KEY cua ban!
    echo.
    echo     Lay API Key mien phi tai:
    echo     https://aistudio.google.com/app/apikey
    echo.
    notepad config.env
)

:: Add to Windows Startup
echo [5/5] Cai dat tu dong khoi dong...
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
echo ==================================================================
echo   [OK] Cai dat hoan tat!
echo
echo   AI Service se TU DONG CHAY khi bat may!
echo
echo   Tiep theo:
echo   1. Kiem tra GEMINI_API_KEY trong config.env
echo   2. Chay start.bat lan dau de test
echo   3. Nhung lan sau chi can mo web dashboard!
echo ==================================================================
echo.
pause
