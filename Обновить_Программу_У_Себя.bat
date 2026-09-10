@echo off
chcp 65001 > nul
title Обновление TouchKey POS Pro
cd /d "%~dp0"
echo 🔄 Обновление установленной программы TouchKey POS...
python update_local_installed.py
pause
