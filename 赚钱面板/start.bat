@echo off
setlocal
set "DIR=%~dp0"
set "PY=C:\Users\石\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not exist "%PY%" ( echo 找不到 Python：%PY% & pause & exit /b 1 )

echo 正在启动本地服务器 http://127.0.0.1:8000 ...
echo 启动后浏览器会自动打开面板；用完关闭这个黑窗口即可停止。
start "" http://127.0.0.1:8000/index.html
"%PY%" -m http.server 8000 --directory "%DIR%"
