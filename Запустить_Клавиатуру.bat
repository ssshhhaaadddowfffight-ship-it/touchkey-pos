@echo off
chcp 65001 > nul
title Запуск TouchKey POS Pro
cd /d "%~dp0"
echo 🚀 Запуск TouchKey POS Pro...
python main.py
