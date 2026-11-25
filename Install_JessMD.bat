@echo off
title Installer Otomatis - JessMD
cd /d "%~dp0"
set "APP_DIR=%~dp0"

echo ========================================================
echo            INSTALASI OTOMATIS JESSMD CONVERTER
echo ========================================================
echo.

:: 1. Deteksi Python (mengabaikan shortcut palsu Microsoft Store)
set "PYTHON_CMD="
py -3 -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
) else (
    python -c "import sys" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python"
    )
)

:: 2. Jika Python belum terpasang, instal otomatis via winget
if "%PYTHON_CMD%"=="" (
    echo [INFO] Python belum terdeteksi di sistem. Menginstal Python 3.12 otomatis...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Gagal menginstal Python otomatis.
        echo Silakan unduh dan instal Python dari https://www.python.org/downloads/
        echo Pastikan mencentang "Add python.exe to PATH", lalu jalankan ulang file ini.
        pause
        exit /b
    )
    set "PYTHON_CMD=py -3"
)

echo [1/4] Membuat virtual environment (venv)...
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
)

echo [2/4] Menginstal library JessMD & OCR (mohon tunggu, butuh koneksi internet)...
"venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Gagal menginstal library. Pastikan koneksi internet stabil lalu coba lagi.
    pause
    exit /b
)

echo [3/4] Mendaftarkan menu klik kanan Windows Explorer...
reg add "HKCU\Software\Classes\*\shell\JessMD_Convert" /ve /t REG_SZ /d "Convert to Markdown (JessMD)" /f >nul
reg add "HKCU\Software\Classes\*\shell\JessMD_Convert" /v "Icon" /t REG_SZ /d "shell32.dll,70" /f >nul
reg add "HKCU\Software\Classes\*\shell\JessMD_Convert\command" /ve /t REG_SZ /d "\"%APP_DIR%venv\Scripts\pythonw.exe\" \"%APP_DIR%context_convert.py\" \"%%1\"" /f >nul

echo [4/4] Membuat shortcut aplikasi di Desktop...
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\JessMD.lnk'); $s.TargetPath = '%APP_DIR%Jalankan_JessMD.bat'; $s.WorkingDirectory = '%APP_DIR%'; $s.IconLocation = 'shell32.dll,70'; $s.Save()" >nul

echo.
echo ========================================================
echo   INSTALASI SELESAI! JessMD siap digunakan.
echo   - Buka Web UI lewat shortcut "JessMD" di Desktop
echo   - Atau klik kanan file dokumen -> Convert to Markdown
echo ========================================================
echo.
pause