@echo off
chcp 65001 > nul
title Kirill - Lotin Telegram Bot
echo ======================================================
echo    Kirill - Lotin Telegram Boti ishga tushmoqda...
echo ======================================================
python bot.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Bot to'xtadi yoki xatolik yuz berdi.
    pause
)


