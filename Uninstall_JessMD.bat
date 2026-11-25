@echo off
title Uninstaller - JessMD
echo Menghapus menu klik kanan Windows Explorer...
reg delete "HKCU\Software\Classes\*\shell\JessMD_Convert" /f >nul 2>&1

echo Menghapus shortcut Desktop...
powershell -NoProfile -Command "$lnk = [Environment]::GetFolderPath('Desktop') + '\JessMD.lnk'; if (Test-Path $lnk) { Remove-Item $lnk -Force }" >nul

echo.
echo Menu dan shortcut JessMD berhasil dihapus.
echo Kamu sekarang bisa menghapus folder JessMD ini secara manual.
pause