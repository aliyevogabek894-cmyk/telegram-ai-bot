@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title Telegram AI - Akkauntni Ulash
cd /d "%~dp0"
echo ==================================================
echo Telegram akkauntga ulanish (Login)
echo ==================================================
python login_new.py
echo.
echo ==================================================
pause
