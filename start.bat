@echo off
setlocal

chcp 65001 >nul
cd /d "%~dp0"
set "ROOT=%~dp0"

echo ==============================================
echo   Videos to Text 一键启动
echo ==============================================


echo [1/2] 启动后端服务 (http://localhost:5000)
start "VideosToText Backend" /D "%ROOT%backend" "%ROOT%.venv\Scripts\python.exe" main.py

echo [2/2] 启动前端服务 (http://localhost:3000)
start "VideosToText Frontend" /D "%ROOT%frontend" cmd /k npm run dev

echo.
echo 启动命令已发送，请等待服务初始化...
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:5000
echo.
pause
