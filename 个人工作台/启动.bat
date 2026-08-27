@echo off
chcp 65001 >nul
title 个人工作台
cd /d "%~dp0"
set "PY=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not exist "%PY%" set "PY=D:\D\python\python.exe"
if not exist "%PY%" set "PY=python"
echo 正在启动个人工作台 ...
start "" "%PY%" app.py
timeout /t 2 /nobreak >nul
start "" http://localhost:8765
echo 已打开浏览器。关闭此窗口即停止工作台。
echo 若浏览器没自动打开，请手动访问 http://localhost:8765
pause
