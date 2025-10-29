FROM python:3.9-slim

LABEL maintainer="ASR Service Team"
LABEL description="FunASR Real-time Speech Recognition Service"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 配置 pip 使用阿里云镜像加速
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 先安装 PyTorch (CPU 版本)
# 使用官方 CPU 版本源，避免安装 GPU 版本
RUN pip install --no-cache-dir torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# 安装其他 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 预下载 FunASR 模型（首次构建时自动下载）
RUN python -c "from funasr import AutoModel; AutoModel(model='paraformer-zh-streaming', model_revision='v2.0.4', device='cpu')"

# 复制应用代码
COPY app.py .
COPY config.py .

# 创建日志目录
RUN mkdir -p logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# 暴露端口
EXPOSE 9999

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9999/health')" || exit 1

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9999", "--workers", "1"]

