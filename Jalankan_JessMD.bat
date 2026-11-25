@"
@echo off
title JessMD - Document to Markdown Converter
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Folder venv tidak ditemukan. Jalankan Install_JessMD.bat terlebih dahulu.
    pause
    exit /b
)

call venv\Scripts\activate.bat
streamlit run app.py
pause
"@ | Set-Content -Path "Jalankan_JessMD.bat" -Encoding ASCII