@echo off
REM 语音实时转录服务启动脚本 (Windows)

REM 切换到脚本所在目录
cd /d "%~dp0"

echo ========================================
echo   语音实时转录服务 - 启动脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    pause
    exit /b 1
)
echo [OK] Python 已安装

REM 检查虚拟环境
if not exist "venv" (
    echo [警告] 虚拟环境不存在，正在创建...
    python -m venv venv
    echo [OK] 虚拟环境创建成功
) else (
    echo [OK] 虚拟环境已存在
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
echo [OK] 虚拟环境已激活

REM 安装依赖
if not exist "venv\deps_installed" (
    echo [警告] 首次运行，正在安装依赖（这可能需要几分钟）...
    python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    echo. > venv\deps_installed
    echo [OK] 依赖安装完成
) else (
    echo [OK] 依赖已安装
)

REM 创建目录
if not exist "logs" mkdir logs
if not exist "models" mkdir models
echo [OK] 目录检查完成

REM 下载模型
echo 检查 FunASR 模型...
python -c "from funasr import AutoModel; AutoModel(model='paraformer-zh-streaming', model_revision='v2.0.4', device='cpu')" 2>nul
if errorlevel 1 (
    echo [警告] 首次运行，正在下载 FunASR 模型（约 300MB）...
    python -c "from funasr import AutoModel; AutoModel(model='paraformer-zh-streaming', model_revision='v2.0.4', device='cpu')"
    echo [OK] 模型下载完成
) else (
    echo [OK] 模型已准备就绪
)

REM 启动服务
echo.
echo ========================================
echo   启动服务...
echo ========================================
echo.
echo 服务地址: http://localhost:9999
echo WebSocket: ws://localhost:9999/ws/asr
echo 测试页面: http://localhost:9999/test
echo.
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause

