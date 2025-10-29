import os
from typing import Optional

class Config:
    """应用配置类"""
    
    # ==================== 服务配置 ====================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 9999))
    
    # ==================== FunASR 模型配置 ====================
    MODEL_NAME: str = os.getenv("MODEL_NAME", "paraformer-zh-streaming")
    MODEL_REVISION: str = os.getenv("MODEL_REVISION", "v2.0.4")
    DEVICE: str = os.getenv("DEVICE", "cpu")  # 使用 CPU
    HOTWORDS: list = os.getenv("HOTWORDS", "").split(",")
    
    # ==================== 音频配置 ====================
    SAMPLE_RATE: int = 16000
    AUDIO_FORMAT: str = "pcm"
    CHUNK_SIZE: int = 8192  # CPU 环境推荐较大的块大小
    
    # ==================== WebSocket 配置 ====================
    WS_TIMEOUT: int = int(os.getenv("WS_TIMEOUT", 300))  # 5分钟
    MAX_MESSAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", 20))  # CPU 环境限制并发
    
    # ==================== 安全配置 ====================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    MAX_AUDIO_SIZE: int = 1 * 1024 * 1024  # 1MB
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "logs/asr.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # ==================== PyTorch 线程配置（CPU 优化）====================
    TORCH_NUM_THREADS: int = int(os.getenv("TORCH_NUM_THREADS", 4))
    OMP_NUM_THREADS: int = int(os.getenv("OMP_NUM_THREADS", 4))
    MKL_NUM_THREADS: int = int(os.getenv("MKL_NUM_THREADS", 4))
    
    @classmethod
    def setup_torch_threads(cls):
        """设置 PyTorch 线程数以优化 CPU 性能"""
        import torch
        torch.set_num_threads(cls.TORCH_NUM_THREADS)
        os.environ["OMP_NUM_THREADS"] = str(cls.OMP_NUM_THREADS)
        os.environ["MKL_NUM_THREADS"] = str(cls.MKL_NUM_THREADS)


# 创建全局配置实例
config = Config()

