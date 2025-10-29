@echo off
chcp 65001 >nul 2>&1
REM 语音实时转录服务 - 停止服务脚本

REM 切换到脚本所在目录
cd /d "%~dp0"

title 停止服务

echo.
echo ========================================================================
echo                        停止语音实时转录服务
echo ========================================================================
echo.

REM 检查运行方式
echo 检测服务运行方式...
echo.

REM 检查 Docker 容器
docker ps | findstr "asr-service" >nul 2>&1
if not errorlevel 1 (
    echo [检测到] Docker 容器正在运行
    echo.
    choice /C YN /M "是否停止 Docker 容器"
    if not errorlevel 2 (
        echo.
        echo 正在停止 Docker 容器...
        docker-compose down
        echo [完成] Docker 容器已停止
    )
)

REM 检查 Python 进程
tasklist | findstr "python.exe" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [检测到] Python 进程正在运行
    echo.
    choice /C YN /M "是否停止所有 Python 进程（可能影响其他 Python 程序）"
    if not errorlevel 2 (
        echo.
        echo 正在停止 Python 进程...
        taskkill /F /IM python.exe >nul 2>&1
        echo [完成] Python 进程已停止
    )
)

echo.
echo ========================================================================
echo                          操作完成
echo ========================================================================
echo.
pause

