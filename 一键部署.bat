@echo off
chcp 65001 >nul 2>&1
REM 语音实时转录服务 - Windows 一键部署脚本
REM 支持直接部署和 Docker 部署两种方式

REM ==================== 重要：切换到脚本所在目录 ====================
cd /d "%~dp0"

title 语音实时转录服务 - 一键部署

echo.
echo ========================================================================
echo                    语音实时转录服务 - 一键部署工具
echo ========================================================================
echo.
echo   版本: v2.1.0
echo   端口: 9999
echo   模式: CPU 优化
echo.
echo ========================================================================
echo.

REM 颜色定义（如果支持）
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM ==================== 检查管理员权限 ====================
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [提示] 检测到管理员权限
) else (
    echo [警告] 建议使用管理员权限运行以避免权限问题
    echo        右键点击此文件，选择"以管理员身份运行"
    echo.
    choice /C YN /M "是否继续（不推荐）"
    if errorlevel 2 goto :end
)

echo.

REM ==================== 主菜单 ====================
:menu
cls
echo.
echo ========================================================================
echo                          选择部署方式
echo ========================================================================
echo.
echo   [1] 直接部署（推荐用于开发测试）
echo       - 使用 Python 虚拟环境
echo       - 便于调试和修改代码
echo       - 适合开发人员
echo.
echo   [2] Docker 部署（推荐用于生产环境）
echo       - 环境隔离，一致性好
echo       - 易于管理和迁移
echo       - 需要安装 Docker Desktop
echo.
echo   [3] 检查系统环境
echo.
echo   [4] 卸载清理
echo.
echo   [0] 退出
echo.
echo ========================================================================
echo.

set /p choice="请选择部署方式 (0-4): "

if "%choice%"=="1" goto :deploy_direct
if "%choice%"=="2" goto :deploy_docker
if "%choice%"=="3" goto :check_env
if "%choice%"=="4" goto :cleanup
if "%choice%"=="0" goto :end

echo [错误] 无效的选择，请重新输入
timeout /t 2 >nul
goto :menu

REM ==================== 方式1: 直接部署 ====================
:deploy_direct
cls
echo.
echo ========================================================================
echo                     方式 1: 直接部署（Python 虚拟环境）
echo ========================================================================
echo.

REM 检查 Python
echo [1/8] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    echo.
    echo 请先安装 Python 3.8 或更高版本：
    echo https://www.python.org/downloads/
    echo.
    pause
    goto :menu
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python 版本: %PYTHON_VERSION%

REM 检查虚拟环境
echo.
echo [2/8] 检查虚拟环境...
if not exist "venv" (
    echo [警告] 虚拟环境不存在，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败！
        pause
        goto :menu
    )
    echo [OK] 虚拟环境创建成功
) else (
    echo [OK] 虚拟环境已存在
)

REM 激活虚拟环境
echo.
echo [3/8] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败！
    pause
    goto :menu
)
echo [OK] 虚拟环境已激活

REM 升级 pip
echo.
echo [4/8] 升级 pip...
python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ >nul 2>&1
echo [OK] pip 已升级

REM 安装依赖
echo.
echo [5/8] 安装项目依赖（这可能需要几分钟）...
if not exist "venv\deps_installed" (
    echo     安装 PyTorch (CPU 版本)...
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
    if errorlevel 1 (
        echo [错误] PyTorch 安装失败！
        pause
        goto :menu
    )
    
    echo     安装其他依赖包...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    if errorlevel 1 (
        echo [错误] 依赖安装失败！
        pause
        goto :menu
    )
    
    echo. > venv\deps_installed
    echo [OK] 所有依赖安装完成
) else (
    echo [OK] 依赖已安装，跳过
)

REM 创建目录
echo.
echo [6/8] 创建必要目录...
if not exist "logs" mkdir logs
if not exist "models" mkdir models
echo [OK] 目录创建完成

REM 下载模型
echo.
echo [7/8] 检查 FunASR 模型...
echo     注意：首次运行会下载约 300MB 的模型文件
python -c "from funasr import AutoModel; AutoModel(model='paraformer-zh-streaming', model_revision='v2.0.4', device='cpu')" >nul 2>&1
if errorlevel 1 (
    echo [警告] 模型未下载，正在下载（约 300MB，请耐心等待）...
    python -c "from funasr import AutoModel; AutoModel(model='paraformer-zh-streaming', model_revision='v2.0.4', device='cpu')"
    if errorlevel 1 (
        echo [错误] 模型下载失败！请检查网络连接
        pause
        goto :menu
    )
    echo [OK] 模型下载完成
) else (
    echo [OK] 模型已下载
)

REM 启动服务
echo.
echo [8/8] 启动服务...
echo.
echo ========================================================================
echo                           服务已准备就绪
echo ========================================================================
echo.
echo   访问地址:
echo   - 主页:        http://localhost:9999
echo   - 健康检查:    http://localhost:9999/health
echo   - 测试页面:    http://localhost:9999/test
echo   - WebSocket:   ws://localhost:9999/ws/asr
echo.
echo   按 Ctrl+C 停止服务
echo.
echo ========================================================================
echo.

timeout /t 3 >nul

REM 启动服务
python app.py

goto :end

REM ==================== 方式2: Docker 部署 ====================
:deploy_docker
cls
echo.
echo ========================================================================
echo                     方式 2: Docker 部署
echo ========================================================================
echo.

REM 检查 Docker
echo [1/5] 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Docker！
    echo.
    echo 请先安装 Docker Desktop for Windows：
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    goto :menu
)

for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo [OK] Docker 版本: %DOCKER_VERSION%

REM 检查 Docker 是否运行
echo.
echo [2/5] 检查 Docker 服务状态...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 服务未运行！
    echo.
    echo 请启动 Docker Desktop，然后重试
    pause
    goto :menu
)
echo [OK] Docker 服务正在运行

REM 询问构建选项
echo.
echo ========================================================================
echo 选择操作：
echo   [1] 构建并启动（首次部署或更新代码后）
echo   [2] 仅启动（已构建过镜像）
echo   [3] 返回主菜单
echo ========================================================================
echo.
set /p docker_choice="请选择 (1-3): "

if "%docker_choice%"=="3" goto :menu
if "%docker_choice%"=="2" goto :docker_start

REM 检查 Dockerfile
echo.
echo [3/5] 检查 Dockerfile...
if not exist "Dockerfile" (
    echo [错误] 找不到 Dockerfile 文件！
    echo.
    echo 当前目录: %CD%
    echo.
    echo 请确保在项目根目录运行此脚本
    echo Dockerfile 应该在项目根目录下
    echo.
    pause
    goto :menu
)
echo [OK] Dockerfile 文件存在

REM 构建镜像
echo.
echo [4/5] 构建 Docker 镜像...
echo     注意：首次构建需要下载基础镜像和模型，需要 10-20 分钟
echo     请确保网络连接稳定
echo     当前目录: %CD%
echo.
timeout /t 3 >nul

echo 开始构建...
docker build -t asr-service:latest .
if errorlevel 1 (
    echo.
    echo [错误] Docker 镜像构建失败！
    echo.
    echo 可能的原因：
    echo   1. 网络问题（无法下载基础镜像）
    echo   2. 配置了 Docker 镜像加速器吗？
    echo.
    echo 解决方法：
    echo   1. 配置 Docker 镜像加速器（Settings - Docker Engine）
    echo   2. 添加以下配置到 registry-mirrors:
    echo      "https://docker.1ms.run"
    echo      "https://dockerhub.icu"
    echo.
    pause
    goto :menu
)
echo [OK] 镜像构建完成

:docker_start
REM 检查 docker-compose.yml
if not exist "docker-compose.yml" (
    echo [错误] 找不到 docker-compose.yml 文件！
    echo 当前目录: %CD%
    pause
    goto :menu
)

REM 停止旧容器
echo.
echo 清理旧容器...
docker-compose down >nul 2>&1
echo [OK] 清理完成

REM 启动容器
echo.
echo 启动 Docker 容器...
docker-compose up -d
if errorlevel 1 (
    echo [错误] 容器启动失败！
    pause
    goto :menu
)

echo.
echo ========================================================================
echo                      Docker 部署成功！
echo ========================================================================
echo.
echo   服务已在后台运行
echo.
echo   访问地址:
echo   - 主页:        http://localhost:9999
echo   - 健康检查:    http://localhost:9999/health
echo   - 测试页面:    http://localhost:9999/test
echo   - WebSocket:   ws://localhost:9999/ws/asr
echo.
echo   管理命令:
echo   - 查看日志:    docker-compose logs -f
echo   - 停止服务:    docker-compose down
echo   - 重启服务:    docker-compose restart
echo.
echo ========================================================================
echo.

choice /C YN /M "是否立即查看日志"
if errorlevel 2 goto :menu
docker-compose logs -f
goto :menu

REM ==================== 检查系统环境 ====================
:check_env
cls
echo.
echo ========================================================================
echo                          系统环境检查
echo ========================================================================
echo.

REM 检查 Python
echo [检查] Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [×] Python: 未安装
    echo     下载地址: https://www.python.org/downloads/
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        echo [√] Python: %%i
    )
)

REM 检查 pip
echo.
echo [检查] pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [×] pip: 未安装
) else (
    for /f "tokens=2" %%i in ('python -m pip --version') do (
        echo [√] pip: %%i
    )
)

REM 检查 Docker
echo.
echo [检查] Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [×] Docker: 未安装
    echo     下载地址: https://www.docker.com/products/docker-desktop/
) else (
    for /f "tokens=3" %%i in ('docker --version') do (
        echo [√] Docker: %%i
    )
    
    REM 检查 Docker 服务
    docker ps >nul 2>&1
    if errorlevel 1 (
        echo [×] Docker 服务: 未运行
    ) else (
        echo [√] Docker 服务: 运行中
    )
)

REM 检查 Docker Compose
echo.
echo [检查] Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [×] Docker Compose: 未安装
) else (
    for /f "tokens=3" %%i in ('docker-compose --version') do (
        echo [√] Docker Compose: %%i
    )
)

REM 检查端口
echo.
echo [检查] 端口 9999 占用情况...
netstat -ano | findstr ":9999" >nul 2>&1
if errorlevel 1 (
    echo [√] 端口 9999: 可用
) else (
    echo [×] 端口 9999: 已被占用
    echo     请关闭占用端口的程序或修改配置文件中的端口
)

REM 检查虚拟环境
echo.
echo [检查] Python 虚拟环境...
if exist "venv" (
    echo [√] 虚拟环境: 已创建
) else (
    echo [×] 虚拟环境: 未创建
)

REM 检查模型
echo.
echo [检查] FunASR 模型...
if exist "%USERPROFILE%\.cache\modelscope" (
    echo [√] 模型缓存目录: 存在
) else (
    echo [×] 模型缓存目录: 不存在（首次运行会自动下载）
)

REM 磁盘空间
echo.
echo [检查] 磁盘空间...
for /f "tokens=3" %%a in ('dir /-c %SystemDrive%\ ^| findstr "bytes free"') do set FREE_SPACE=%%a
echo [√] 可用空间: %FREE_SPACE% 字节

echo.
echo ========================================================================
echo                          检查完成
echo ========================================================================
echo.
pause
goto :menu

REM ==================== 卸载清理 ====================
:cleanup
cls
echo.
echo ========================================================================
echo                          卸载清理
echo ========================================================================
echo.
echo [警告] 此操作将删除以下内容：
echo   - Python 虚拟环境 (venv/)
echo   - 日志文件 (logs/)
echo   - Docker 镜像和容器
echo   - 模型文件将保留在 %USERPROFILE%\.cache\modelscope\
echo.
echo ========================================================================
echo.

choice /C YN /M "确定要继续吗"
if errorlevel 2 goto :menu

echo.
echo [1/4] 停止运行中的服务...
REM 停止 Docker 容器
docker-compose down >nul 2>&1
REM 停止可能运行的 Python 进程
taskkill /F /IM python.exe /FI "WINDOWTITLE eq 语音实时转录服务*" >nul 2>&1
echo [OK] 服务已停止

echo.
echo [2/4] 删除虚拟环境...
if exist "venv" (
    rmdir /s /q venv
    echo [OK] 虚拟环境已删除
) else (
    echo [跳过] 虚拟环境不存在
)

echo.
echo [3/4] 删除日志文件...
if exist "logs" (
    rmdir /s /q logs
    echo [OK] 日志文件已删除
) else (
    echo [跳过] 日志目录不存在
)

echo.
echo [4/4] 删除 Docker 镜像...
docker rmi asr-service:latest >nul 2>&1
if errorlevel 1 (
    echo [跳过] Docker 镜像不存在或未安装 Docker
) else (
    echo [OK] Docker 镜像已删除
)

echo.
echo ========================================================================
echo                          清理完成
echo ========================================================================
echo.
echo 如需完全清理（包括模型文件），请手动删除：
echo %USERPROFILE%\.cache\modelscope\
echo.
pause
goto :menu

REM ==================== 退出 ====================
:end
echo.
echo 感谢使用！
echo.
pause
exit /b 0

