([简体中文](./README.md) | [English](./README_EN.md))

<div align="center">

# 🎙️ 语音实时转录服务

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![FunASR](https://img.shields.io/badge/FunASR-1.0+-orange.svg)](https://github.com/modelscope/FunASR)
[![Docker](https://img.shields.io/badge/Docker-supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**基于 FunASR 的实时语音转录后端服务，支持 PTT 模式和 WebSocket 实时通信**

[快速开始](#快速开始) | [功能特性](#功能特性) | [在线演示](#在线演示) | [文档](#文档) | [常见问题](#常见问题)

</div>

---

## 📖 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [在线演示](#在线演示)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [一键部署](#一键部署)
  - [Docker 部署](#docker-部署)
  - [手动部署](#手动部署)
- [使用示例](#使用示例)
- [API 文档](#api-文档)
- [性能指标](#性能指标)
- [技术架构](#技术架构)
- [文档](#文档)
- [常见问题](#常见问题)
- [更新日志](#更新日志)
- [贡献指南](#贡献指南)
- [致谢](#致谢)
- [许可证](#许可证)

---

## 简介

本项目是一个高性能的实时语音转录后端服务，基于阿里达摩院开源的 [FunASR](https://github.com/modelscope/FunASR) 引擎开发。采用 PTT（Push-to-Talk，按住说话）模式，通过 WebSocket 协议实现低延迟的双向通信，专为实时语音识别场景设计。

### 🎯 核心优势

- **🚀 快速响应**：模型常驻内存，识别延迟 < 1000ms（CPU 环境）
- **💡 智能控制**：PTT 模式精确控制，按需识别，节省资源
- **🔧 易于部署**：纯 CPU 环境，支持 Docker 一键部署
- **📊 生产就绪**：支持负载均衡、健康检查、详细日志
- **🌐 标准协议**：基于 WebSocket，易于集成各类前端
- **🎨 开箱即用**：提供测试页面，快速验证功能

---

## 功能特性

### ✨ 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **实时语音识别** | 基于 FunASR paraformer-zh-streaming 模型 | ✅ |
| **PTT 模式** | 支持 start/stop/reset 控制指令 | ✅ |
| **WebSocket 通信** | 低延迟双向实时通信 | ✅ |
| **流式处理** | 边接收边识别，实时返回结果 | ✅ |
| **多用户并发** | 支持 10-20 并发连接（CPU 环境） | ✅ |
| **模型常驻** | 预加载模型，空闲时不消耗计算资源 | ✅ |

### 🔌 接口支持

- **WebSocket 接口**：`/ws/asr` - 语音识别主接口
- **HTTP 接口**：
  - `/` - 服务信息
  - `/health` - 健康检查
  - `/stats` - 统计信息
  - `/test` - 测试页面

### 📦 部署方式

- ✅ **直接部署**：Python 虚拟环境，适合开发调试
- ✅ **Docker 部署**：容器化部署，适合生产环境
- ✅ **一键部署**：Windows/Linux 脚本，零配置启动

### 🎯 支持的音频格式

| 参数 | 值 |
|------|---|
| 采样率 | 16000 Hz |
| 声道数 | 1（单声道） |
| 编码格式 | PCM |
| 位深度 | 16 bit (INT16) |
| 传输编码 | Base64 |

---

## 在线演示

服务启动后，访问测试页面即可体验：

```
http://localhost:9999/test
```

![测试页面示例](./docs/images/demo.png)

> 📝 **注意**：测试页面提供了完整的 WebSocket 交互示例，包括连接管理、控制指令发送、消息接收等。

---

## 快速开始

### 环境要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **操作系统** | Windows 10+ / Ubuntu 20.04+ / CentOS 7+ | - |
| **Python** | 3.8+ | 3.9+ |
| **CPU** | 2 核心 | 4 核心+ |
| **内存** | 4GB | 8GB+ |
| **磁盘** | 10GB | 20GB+ |
| **Docker** (可选) | 20.10+ | 最新版本 |

### 一键部署

#### Windows

```batch
# 右键"以管理员身份运行"
一键部署.bat

# 选择部署方式：
# [1] 直接部署 - 适合开发
# [2] Docker 部署 - 适合生产
```

#### Linux/macOS

```bash
# 赋予执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

服务启动后访问：
- 主页：http://localhost:9999
- 测试页面：http://localhost:9999/test
- 健康检查：http://localhost:9999/health

### Docker 部署

#### 方式 1：使用 Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone <repository_url>
cd asr

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

#### 方式 2：使用 Docker 命令

```bash
# 构建镜像
docker build -t asr-service:latest .

# 运行容器
docker run -d \
  --name asr-service \
  -p 9999:9999 \
  -v $(pwd)/models:/root/.cache/modelscope \
  -v $(pwd)/logs:/app/logs \
  asr-service:latest

# 查看日志
docker logs -f asr-service
```

### 手动部署

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. 安装 PyTorch (CPU 版本)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. 安装其他依赖
pip install -r requirements.txt

# 4. 启动服务
python app.py
```

---

## 使用示例

### Python 客户端示例

```python
import asyncio
import websockets
import json
import base64
import numpy as np

async def test_asr():
    uri = "ws://localhost:9999/ws/asr"
    
    async with websockets.connect(uri) as websocket:
        # 1. 接收连接确认
        response = await websocket.recv()
        print(f"连接成功: {response}")
        
        # 2. 发送 start 指令
        await websocket.send(json.dumps({
            "type": "control",
            "command": "start",
            "timestamp": int(time.time() * 1000)
        }))
        
        # 3. 发送音频数据
        # 假设 audio_data 是 16kHz, 单声道, PCM 格式的音频
        audio_base64 = base64.b64encode(audio_data).decode()
        await websocket.send(json.dumps({
            "type": "audio",
            "data": audio_base64,
            "timestamp": int(time.time() * 1000)
        }))
        
        # 4. 接收识别结果
        result = await websocket.recv()
        result_json = json.loads(result)
        print(f"识别结果: {result_json['text']}")
        
        # 5. 发送 stop 指令
        await websocket.send(json.dumps({
            "type": "control",
            "command": "stop",
            "timestamp": int(time.time() * 1000)
        }))

asyncio.run(test_asr())
```

### JavaScript 客户端示例

```javascript
// 建立 WebSocket 连接
const ws = new WebSocket('ws://localhost:9999/ws/asr');

ws.onopen = () => {
    console.log('WebSocket 连接已建立');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'result') {
        console.log('识别结果:', data.text);
    } else if (data.type === 'status') {
        console.log('状态:', data.message);
    }
};

// 发送开始指令
function startRecording() {
    ws.send(JSON.stringify({
        type: 'control',
        command: 'start',
        timestamp: Date.now()
    }));
}

// 发送音频数据
function sendAudio(audioData) {
    // audioData 应该是 Base64 编码的 PCM 数据
    ws.send(JSON.stringify({
        type: 'audio',
        data: audioData,
        timestamp: Date.now()
    }));
}

// 发送停止指令
function stopRecording() {
    ws.send(JSON.stringify({
        type: 'control',
        command: 'stop',
        timestamp: Date.now()
    }));
}
```

### cURL 测试健康检查

```bash
# 健康检查
curl http://localhost:9999/health

# 服务信息
curl http://localhost:9999/

# 统计信息
curl http://localhost:9999/stats
```

---

## API 文档

### WebSocket 协议

#### 连接地址
```
ws://[server_ip]:9999/ws/asr
```

#### 客户端 → 服务端

**控制指令**
```json
{
  "type": "control",
  "command": "start|stop|reset",
  "timestamp": 1698756432000
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 消息类型，固定为 "control" |
| command | string | 是 | 控制命令：start(开始) / stop(停止) / reset(重置) |
| timestamp | integer | 否 | 时间戳（毫秒） |

**音频数据**
```json
{
  "type": "audio",
  "data": "base64_encoded_pcm_data",
  "timestamp": 1698756432000
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 消息类型，固定为 "audio" |
| data | string | 是 | Base64 编码的 PCM 音频数据 |
| timestamp | integer | 否 | 时间戳（毫秒） |

#### 服务端 → 客户端

**识别结果**
```json
{
  "type": "result",
  "mode": "partial",
  "text": "识别的文本内容",
  "timestamp": 1698756432000,
  "confidence": 0.95,
  "processing_time_ms": 125.5
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 消息类型，固定为 "result" |
| mode | string | 结果模式：partial(部分) / final(最终) |
| text | string | 识别出的文本内容 |
| timestamp | integer | 时间戳（毫秒） |
| confidence | float | 置信度（0-1） |
| processing_time_ms | float | 处理耗时（毫秒） |

**状态消息**
```json
{
  "type": "status",
  "code": 200,
  "message": "连接成功",
  "timestamp": 1698756432000
}
```

**错误消息**
```json
{
  "type": "error",
  "code": 500,
  "message": "错误描述",
  "timestamp": 1698756432000
}
```

### HTTP 接口

| 端点 | 方法 | 说明 | 响应 |
|------|------|------|------|
| `/` | GET | 服务信息 | JSON |
| `/health` | GET | 健康检查 | JSON |
| `/stats` | GET | 统计信息 | JSON |
| `/test` | GET | 测试页面 | HTML |

---

## 性能指标

### CPU 环境（4核心 / 8GB 内存）

| 指标 | 数值 | 说明 |
|------|------|------|
| **识别延迟** | < 1000ms | 单次识别的端到端延迟 |
| **并发连接** | 10-20 | 同时支持的 WebSocket 连接数 |
| **CPU 使用率** | 40-60% | 满负载时的 CPU 占用 |
| **内存占用** | ~4GB | 模型加载后的内存使用 |
| **识别准确率** | ≥ 95% | 标准普通话环境 |

### GPU 环境（可选）

| 指标 | 数值 | 说明 |
|------|------|------|
| **识别延迟** | < 300ms | 使用 GPU 加速 |
| **并发连接** | 50-100 | GPU 环境下的并发能力 |
| **GPU 使用率** | 30-50% | 满负载时的 GPU 占用 |

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    前端（WebSocket Client）                   │
│            发送音频数据 + 控制指令 (start/stop)                │
└─────────────────────────────────────────────────────────────┘
                          ↓ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                    后端接口服务（FastAPI）                     │
├─────────────────────────────────────────────────────────────┤
│  Web 服务层                                                   │
│  ┌─────────────────────────────────────────┐                │
│  │  FastAPI + WebSocket Handler           │                │
│  │  • 接受 WebSocket 连接                  │                │
│  │  • 路由：/ws/asr                        │                │
│  └─────────────────────────────────────────┘                │
│                          ↓                                    │
│  业务逻辑层                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ 连接管理   │  │ 音频处理   │  │ 结果封装   │            │
│  │• 多连接    │  │• Base64解码│  │• JSON封装  │            │
│  │• 状态跟踪  │  │• PCM转换   │  │• 时间戳    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                          ↓                                    │
│  语音识别层 (FunASR)                                          │
│  ┌─────────────────────────────────────────┐                │
│  │   FunASR 模型（常驻内存）                 │                │
│  │   • paraformer-zh-streaming             │                │
│  │   • 应用启动时加载                       │                │
│  │   • 接收音频时调用 generate()            │                │
│  │   • 无音频时空闲，不消耗计算资源          │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| **编程语言** | Python | 3.8+ |
| **Web 框架** | FastAPI | 0.104+ |
| **WebSocket** | websockets | 12.0+ |
| **ASR 引擎** | FunASR | 1.0+ |
| **深度学习** | PyTorch | 2.1.0 (CPU) |
| **音频处理** | soundfile, numpy | - |
| **容器化** | Docker, Docker Compose | - |

---

## 文档

- [📘 开发文档](./开发文档.md) - 详细的技术设计和实现说明
- [📗 部署文档](./部署文档.md) - 完整的部署指南和运维手册
- [📙 快速启动指南](./快速启动指南.md) - 5分钟快速上手
- [📕 Windows 使用说明](./Windows使用说明.md) - Windows 平台专用指南
- [📊 项目交付清单](./项目交付清单.md) - 功能清单和验证步骤

---

## 常见问题

<details>
<summary><b>Q: 模型下载很慢怎么办？</b></summary>

A: 模型会自动从 ModelScope 下载。如果下载慢，可以：
1. 使用代理或 VPN
2. 手动下载模型到 `~/.cache/modelscope/` 目录
3. 等待自动重试

</details>

<details>
<summary><b>Q: 如何提高并发连接数？</b></summary>

A: 
1. 增加服务器 CPU 核心数
2. 部署多个实例 + Nginx 负载均衡
3. 使用 GPU 加速（可提升 3-5 倍性能）
4. 调整 `MAX_CONNECTIONS` 环境变量

</details>

<details>
<summary><b>Q: 支持其他语言吗？</b></summary>

A: 支持！修改 `MODEL_NAME` 环境变量即可：
- 中文：`paraformer-zh-streaming`
- 英文：`paraformer-en-streaming`

</details>

<details>
<summary><b>Q: Docker 构建失败怎么办？</b></summary>

A: 
1. 配置 Docker 镜像加速器
2. 检查网络连接
3. 查看详细错误日志
4. 参考 [Windows使用说明.md](./Windows使用说明.md)

</details>

<details>
<summary><b>Q: CPU 环境性能如何？</b></summary>

A: 
- 单次识别延迟：500-1000ms
- 并发连接：10-20 个
- 适合中小规模应用
- 建议使用 GPU 提升性能

</details>

<details>
<summary><b>Q: 如何在生产环境部署？</b></summary>

A: 推荐配置：
1. 使用 Docker Compose 部署
2. 配置 Nginx 反向代理
3. 启用 HTTPS/WSS
4. 部署多实例 + 负载均衡
5. 配置监控和日志

详见 [部署文档](./部署文档.md)

</details>

---

## 更新日志

### v2.1.0 (2024-10-28)

#### 新增
- ✨ Windows 一键部署脚本
- ✨ 完整的测试工具集
- ✨ 详细的使用文档

#### 优化
- 🔧 优化为纯 CPU 部署方案
- 🔧 Docker 镜像使用阿里云源
- 🔧 分步安装 PyTorch，避免版本冲突
- 🔧 所有脚本自动切换到正确目录

#### 修复
- 🐛 修复 Docker 部署路径问题
- 🐛 修复批处理脚本目录切换问题

### v2.0.0 (2024-10-28)

- 🎉 首次发布
- ✨ 支持 PTT 模式
- ✨ WebSocket 实时通信
- ✨ Docker 部署支持

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 代码风格：遵循 PEP 8
- 提交信息：使用语义化提交规范
- 测试：添加必要的单元测试
- 文档：更新相关文档

---

## 致谢

本项目基于以下优秀的开源项目：

- [FunASR](https://github.com/modelscope/FunASR) - 阿里达摩院开源的语音识别工具包
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [ModelScope](https://www.modelscope.cn/) - 模型托管平台

感谢所有贡献者的支持！

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](./LICENSE) 文件

---

<div align="center">

**如果这个项目对您有帮助，请给一个 ⭐️ Star！**

Made with ❤️ by Hurrvey

</div>
