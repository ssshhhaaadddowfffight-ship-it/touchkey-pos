@echo off
chcp 65001 > nul
title Сборка TouchKey_POS_Setup.exe
cd /d "%~dp0"
echo 📦 Сборка установщика TouchKey_POS_Setup.exe...
python build_installer_exe.py
pause
