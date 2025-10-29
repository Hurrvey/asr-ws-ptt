#!/bin/bash
# 语音实时转录服务启动脚本

set -e

echo "========================================"
echo "  语音实时转录服务 - 启动脚本"
echo "========================================"
echo ""

# 检查 Python 版本
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ 错误: 未找到 Python3"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python 版本: $python_version"
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "venv" ]; then
        echo "⚠ 虚拟环境不存在，正在创建..."
        python3 -m venv venv
        echo "✓ 虚拟环境创建成功"
    else
        echo "✓ 虚拟环境已存在"
    fi
}

# 激活虚拟环境
activate_venv() {
    echo "激活虚拟环境..."
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
}

# 安装依赖
install_deps() {
    echo "检查依赖..."
    if [ ! -f "venv/deps_installed" ]; then
        echo "⚠ 首次运行，正在安装依赖（这可能需要几分钟）..."
        pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
        pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
        pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
        touch venv/deps_installed
        echo "✓ 依赖安装完成"
    else
        echo "✓ 依赖已安装"
    fi
}

# 下载模型
download_model() {
    echo "检查 FunASR 模型..."
    if [ ! -d "$HOME/.cache/modelscope/hub" ]; then
        echo "⚠ 首次运行，正在下载 FunASR 模型（约 300MB）..."
        python -c "from funasr import AutoModel; AutoModel(model='paraformer-zh-streaming', model_revision='v2.0.4', device='cpu')"
        echo "✓ 模型下载完成"
    else
        echo "✓ 模型已下载"
    fi
}

# 创建必要目录
create_dirs() {
    mkdir -p logs
    mkdir -p models
    echo "✓ 目录检查完成"
}

# 启动服务
start_service() {
    echo ""
    echo "========================================"
    echo "  启动服务..."
    echo "========================================"
    echo ""
    echo "服务地址: http://0.0.0.0:9999"
    echo "WebSocket: ws://0.0.0.0:9999/ws/asr"
    echo "测试页面: http://localhost:9999/test"
    echo ""
    echo "按 Ctrl+C 停止服务"
    echo ""
    
    # 启动服务
    python app.py
}

# 主流程
main() {
    check_python
    check_venv
    activate_venv
    install_deps
    create_dirs
    download_model
    start_service
}

# 捕获中断信号
trap 'echo ""; echo "服务已停止"; exit 0' INT TERM

# 运行
main

