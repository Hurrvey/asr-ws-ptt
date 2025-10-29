@echo off
chcp 65001 >nul 2>&1
REM 语音实时转录服务 - 快速测试脚本

REM 切换到脚本所在目录
cd /d "%~dp0"

title 语音实时转录服务 - 快速测试

echo.
echo ========================================================================
echo                    语音实时转录服务 - 快速测试
echo ========================================================================
echo.

REM 检查服务是否运行
echo [1/3] 检查服务状态...
curl -s http://localhost:9999/health >nul 2>&1
if errorlevel 1 (
    echo [错误] 服务未运行！
    echo.
    echo 请先运行以下命令启动服务：
    echo   - 直接部署: start.bat 或 一键部署.bat
    echo   - Docker:   docker-compose up -d
    echo.
    pause
    exit /b 1
)
echo [OK] 服务正在运行

REM 显示服务信息
echo.
echo [2/3] 获取服务信息...
echo.
curl -s http://localhost:9999/ | python -m json.tool 2>nul
if errorlevel 1 (
    echo [警告] 无法解析 JSON，使用原始输出：
    curl -s http://localhost:9999/
)

REM 健康检查
echo.
echo [3/3] 健康检查...
echo.
curl -s http://localhost:9999/health | python -m json.tool 2>nul
if errorlevel 1 (
    curl -s http://localhost:9999/health
)

echo.
echo ========================================================================
echo                          测试完成
echo ========================================================================
echo.
echo 访问地址：
echo   - 主页:        http://localhost:9999
echo   - 测试页面:    http://localhost:9999/test
echo   - WebSocket:   ws://localhost:9999/ws/asr
echo.
echo 运行自动化测试：
echo   python test_client.py
echo.
echo ========================================================================
echo.

choice /C YN /M "是否在浏览器中打开测试页面"
if errorlevel 2 goto :end

start http://localhost:9999/test

:end
pause

