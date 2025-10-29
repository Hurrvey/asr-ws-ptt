"""
语音实时转录接口 - PTT模式
支持 WebSocket 实时双向通信,基于 FunASR 进行中文语音识别
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from funasr import AutoModel
import json
import base64
import numpy as np
from typing import Dict, Optional
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import asyncio
from datetime import datetime

from config import config

# ==================== 日志配置 ====================
os.makedirs('logs', exist_ok=True)

logger = logging.getLogger("asr_service")
logger.setLevel(getattr(logging, config.LOG_LEVEL))

# 文件处理器（自动轮转）
file_handler = RotatingFileHandler(
    config.LOG_FILE,
    maxBytes=config.LOG_MAX_BYTES,
    backupCount=config.LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
logger.addHandler(console_handler)

# ==================== FastAPI 应用 ====================
app = FastAPI(
    title="语音实时转录接口 - PTT模式",
    description="基于 FunASR 的实时语音转录 WebSocket 接口",
    version="2.1.0"
)

# ==================== 全局变量 ====================
# 存储 WebSocket 连接
connections: Dict[int, WebSocket] = {}

# 全局 FunASR 模型实例（应用启动时加载并常驻内存）
asr_model: Optional[AutoModel] = None


# ==================== 应用生命周期事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global asr_model
    
    logger.info("=" * 60)
    logger.info("语音实时转录服务启动中...")
    logger.info(f"部署模式: CPU")
    logger.info(f"模型: {config.MODEL_NAME}")
    logger.info(f"最大并发连接: {config.MAX_CONNECTIONS}")
    logger.info("=" * 60)
    
    # 设置 PyTorch 线程数优化 CPU 性能
    config.setup_torch_threads()
    logger.info(f"PyTorch 线程数设置为: {config.TORCH_NUM_THREADS}")
    
    # 加载 FunASR 模型
    logger.info("正在加载 FunASR 模型（CPU模式，常驻后台）...")
    try:
        asr_model = AutoModel(
            model=config.MODEL_NAME,
            model_revision=config.MODEL_REVISION,
            device=config.DEVICE
        )
        logger.info("✓ FunASR 模型加载成功（CPU模式），已常驻后台，等待调用")
    except Exception as e:
        logger.error(f"✗ 模型加载失败: {e}")
        raise
    
    logger.info("=" * 60)
    logger.info("服务启动完成，等待 WebSocket 连接...")
    logger.info(f"WebSocket 端点: ws://{config.HOST}:{config.PORT}/ws/asr")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    logger.info("服务正在关闭...")
    # 关闭所有 WebSocket 连接
    for connection_id, websocket in list(connections.items()):
        try:
            await websocket.close()
            logger.info(f"关闭连接: {connection_id}")
        except:
            pass
    connections.clear()
    logger.info("服务已关闭")


# ==================== 音频处理器 ====================
class AudioProcessor:
    """音频处理器 - 负责音频数据的解码和预处理"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.audio_buffer = []
        
    def decode_audio(self, audio_data: str) -> Optional[np.ndarray]:
        """
        解码 base64 音频数据为 numpy 数组
        
        Args:
            audio_data: base64 编码的音频数据
            
        Returns:
            numpy 数组（float32）或 None（解码失败时）
        """
        try:
            # Base64 解码
            audio_bytes = base64.b64decode(audio_data)
            
            # 转换为 int16 数组
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # 转换为 float32 并归一化到 [-1, 1]
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            return audio_float
        except Exception as e:
            logger.error(f"音频解码失败: {e}")
            return None
    
    def clear_buffer(self):
        """清空音频缓冲区"""
        self.audio_buffer = []
        logger.debug("音频缓冲区已清空")


# ==================== WebSocket 端点 ====================
@app.websocket("/ws/asr")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端点：处理实时语音识别（PTT模式）
    
    协议说明:
    - 客户端发送: {"type": "control", "command": "start|stop|reset", "timestamp": ...}
    - 客户端发送: {"type": "audio", "data": "base64...", "timestamp": ...}
    - 服务端返回: {"type": "result|status|error", ...}
    """
    
    # 检查连接数限制
    if len(connections) >= config.MAX_CONNECTIONS:
        await websocket.close(code=1008, reason="服务器连接已满，请稍后重试")
        logger.warning(f"连接被拒绝：已达到最大连接数 {config.MAX_CONNECTIONS}")
        return
    
    # 接受 WebSocket 连接
    await websocket.accept()
    
    # 生成唯一连接 ID
    connection_id = id(websocket)
    connections[connection_id] = websocket
    
    # 创建音频处理器
    audio_processor = AudioProcessor(sample_rate=config.SAMPLE_RATE)
    
    # PTT 模式状态标志
    is_recording = False
    
    # 统计信息
    stats = {
        "start_time": time.time(),
        "audio_chunks": 0,
        "recognitions": 0,
        "errors": 0
    }
    
    logger.info(f"新连接建立: {connection_id} | 当前连接数: {len(connections)}")
    
    # 发送连接成功消息
    try:
        await websocket.send_json({
            "type": "status",
            "code": 200,
            "message": "连接成功，FunASR已就绪",
            "connection_id": str(connection_id),
            "timestamp": int(time.time() * 1000)
        })
    except Exception as e:
        logger.error(f"[{connection_id}] 发送连接确认失败: {e}")
        return
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            timestamp = message.get("timestamp", int(time.time() * 1000))
            
            # ==================== 处理音频数据 ====================
            if msg_type == "audio":
                # 只有在录音状态（按住按钮）时才处理音频
                if not is_recording:
                    logger.debug(f"[{connection_id}] 收到音频数据但未在录音状态，忽略")
                    continue
                
                audio_data = message.get("data")
                
                if not audio_data:
                    logger.warning(f"[{connection_id}] 收到空音频数据")
                    continue
                
                # 检查音频数据大小
                if len(audio_data) > config.MAX_AUDIO_SIZE:
                    await websocket.send_json({
                        "type": "error",
                        "code": 413,
                        "message": "音频数据过大",
                        "timestamp": int(time.time() * 1000)
                    })
                    stats["errors"] += 1
                    continue
                
                # 解码音频
                audio_chunk = audio_processor.decode_audio(audio_data)
                
                if audio_chunk is not None and len(audio_chunk) > 0:
                    stats["audio_chunks"] += 1
                    
                    # 调用 FunASR 进行识别
                    try:
                        start_time = time.time()
                        logger.debug(f"[{connection_id}] 调用 FunASR 识别（音频长度: {len(audio_chunk)}）...")
                        
                        # 调用模型进行识别
                        result = asr_model.generate(
                            input=audio_chunk,
                            batch_size=1,
                            disable_pbar=True,
                            hotwords=config.HOTWORDS
                        )
                        
                        recognition_time = (time.time() - start_time) * 1000  # 毫秒
                        
                        if result and len(result) > 0:
                            text = result[0].get("text", "")
                            
                            if text.strip():
                                stats["recognitions"] += 1
                                
                                # 返回识别结果
                                await websocket.send_json({
                                    "type": "result",
                                    "mode": "partial",
                                    "text": text,
                                    "timestamp": timestamp,
                                    "confidence": 0.95,
                                    "processing_time_ms": round(recognition_time, 2)
                                })
                                
                                logger.info(
                                    f"[{connection_id}] 识别结果: {text} "
                                    f"(耗时: {recognition_time:.2f}ms)"
                                )
                            else:
                                logger.debug(f"[{connection_id}] 识别结果为空")
                        else:
                            logger.debug(f"[{connection_id}] 未获取到识别结果")
                            
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"[{connection_id}] 识别错误: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "code": 500,
                            "message": f"识别失败: {str(e)}",
                            "timestamp": int(time.time() * 1000)
                        })
            
            # ==================== 处理控制指令 ====================
            elif msg_type == "control":
                command = message.get("command")
                
                if command == "start":
                    # 用户按下按钮，开始录音
                    is_recording = True
                    audio_processor.clear_buffer()
                    logger.info(f"[{connection_id}] ▶ 开始录音（按钮按下）")
                    
                    await websocket.send_json({
                        "type": "status",
                        "code": 200,
                        "message": "开始录音",
                        "timestamp": int(time.time() * 1000)
                    })
                
                elif command == "stop":
                    # 用户松开按钮，停止录音
                    is_recording = False
                    logger.info(f"[{connection_id}] ⏸ 停止录音（按钮松开），FunASR回到空闲")
                    
                    await websocket.send_json({
                        "type": "status",
                        "code": 200,
                        "message": "停止录音",
                        "timestamp": int(time.time() * 1000)
                    })
                
                elif command == "reset":
                    # 重置状态
                    is_recording = False
                    audio_processor.clear_buffer()
                    logger.info(f"[{connection_id}] 🔄 重置状态")
                    
                    await websocket.send_json({
                        "type": "status",
                        "code": 200,
                        "message": "重置成功",
                        "timestamp": int(time.time() * 1000)
                    })
                
                else:
                    logger.warning(f"[{connection_id}] 未知控制指令: {command}")
                    await websocket.send_json({
                        "type": "error",
                        "code": 400,
                        "message": f"未知控制指令: {command}",
                        "timestamp": int(time.time() * 1000)
                    })
            
            # ==================== 处理未知消息类型 ====================
            else:
                logger.warning(f"[{connection_id}] 未知消息类型: {msg_type}")
                await websocket.send_json({
                    "type": "error",
                    "code": 400,
                    "message": f"未知消息类型: {msg_type}",
                    "timestamp": int(time.time() * 1000)
                })
    
    except WebSocketDisconnect:
        # 连接正常断开
        duration = time.time() - stats["start_time"]
        logger.info(
            f"连接断开: {connection_id} | "
            f"持续时间: {duration:.2f}s | "
            f"音频块: {stats['audio_chunks']} | "
            f"识别次数: {stats['recognitions']} | "
            f"错误: {stats['errors']}"
        )
        
    except Exception as e:
        # 异常错误
        stats["errors"] += 1
        logger.error(f"[{connection_id}] WebSocket 错误: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "code": 500,
                "message": f"服务器错误: {str(e)}",
                "timestamp": int(time.time() * 1000)
            })
        except:
            pass
    
    finally:
        # 清理连接
        if connection_id in connections:
            del connections[connection_id]
        logger.info(f"连接清理完成: {connection_id} | 剩余连接数: {len(connections)}")


# ==================== HTTP 端点 ====================
@app.get("/")
async def root():
    """根路径 - 返回服务信息"""
    return {
        "service": "语音实时转录接口",
        "version": "2.1.0",
        "mode": "PTT (Push-to-Talk)",
        "model": config.MODEL_NAME,
        "device": config.DEVICE,
        "endpoint": f"ws://{config.HOST}:{config.PORT}/ws/asr",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    return {
        "status": "healthy",
        "model_loaded": asr_model is not None,
        "active_connections": len(connections),
        "max_connections": config.MAX_CONNECTIONS,
        "cpu_usage_percent": cpu_percent,
        "memory_usage_percent": memory.percent,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """获取服务统计信息"""
    return {
        "active_connections": len(connections),
        "max_connections": config.MAX_CONNECTIONS,
        "model": config.MODEL_NAME,
        "device": config.DEVICE,
        "sample_rate": config.SAMPLE_RATE
    }


@app.get("/test")
async def test_page():
    """测试页面 - 提供简单的 WebSocket 测试界面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ASR WebSocket 测试</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .container {
                border: 1px solid #ddd;
                padding: 20px;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                margin: 5px;
                font-size: 16px;
                cursor: pointer;
            }
            #status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 3px;
            }
            .connected {
                background-color: #d4edda;
                color: #155724;
            }
            .disconnected {
                background-color: #f8d7da;
                color: #721c24;
            }
            #messages {
                height: 300px;
                overflow-y: scroll;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 10px 0;
                background-color: #f8f9fa;
            }
            .message {
                margin: 5px 0;
                padding: 5px;
                border-left: 3px solid #007bff;
                background-color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>语音实时转录 WebSocket 测试</h1>
            <div id="status" class="disconnected">未连接</div>
            
            <div>
                <button onclick="connect()">连接</button>
                <button onclick="disconnect()">断开</button>
                <button onclick="sendStart()">发送 Start</button>
                <button onclick="sendStop()">发送 Stop</button>
                <button onclick="clearMessages()">清空消息</button>
            </div>
            
            <h3>消息日志:</h3>
            <div id="messages"></div>
        </div>

        <script>
            let ws = null;
            const statusEl = document.getElementById('status');
            const messagesEl = document.getElementById('messages');

            function addMessage(msg, type = 'info') {
                const div = document.createElement('div');
                div.className = 'message';
                div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
                messagesEl.appendChild(div);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }

            function connect() {
                if (ws) {
                    addMessage('已经连接', 'warning');
                    return;
                }

                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/asr`;
                
                addMessage(`正在连接: ${wsUrl}`);
                ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    statusEl.textContent = '已连接';
                    statusEl.className = 'connected';
                    addMessage('WebSocket 连接成功');
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    addMessage(`收到消息: ${JSON.stringify(data, null, 2)}`);
                };

                ws.onerror = (error) => {
                    addMessage(`错误: ${error}`, 'error');
                };

                ws.onclose = () => {
                    statusEl.textContent = '未连接';
                    statusEl.className = 'disconnected';
                    addMessage('WebSocket 连接已关闭');
                    ws = null;
                };
            }

            function disconnect() {
                if (!ws) {
                    addMessage('未连接', 'warning');
                    return;
                }
                ws.close();
            }

            function sendStart() {
                if (!ws) {
                    addMessage('请先连接', 'warning');
                    return;
                }
                const msg = {
                    type: 'control',
                    command: 'start',
                    timestamp: Date.now()
                };
                ws.send(JSON.stringify(msg));
                addMessage(`发送: ${JSON.stringify(msg)}`);
            }

            function sendStop() {
                if (!ws) {
                    addMessage('请先连接', 'warning');
                    return;
                }
                const msg = {
                    type: 'control',
                    command: 'stop',
                    timestamp: Date.now()
                };
                ws.send(JSON.stringify(msg));
                addMessage(`发送: ${JSON.stringify(msg)}`);
            }

            function clearMessages() {
                messagesEl.innerHTML = '';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )

