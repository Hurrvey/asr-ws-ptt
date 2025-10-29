([简体中文](./README.md) | [English](./README_EN.md))

<div align="center">

# 🎙️ Real-time Speech Transcription Service

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![FunASR](https://img.shields.io/badge/FunASR-1.0+-orange.svg)](https://github.com/modelscope/FunASR)
[![Docker](https://img.shields.io/badge/Docker-supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**Real-time Speech Transcription Backend Service Based on FunASR, Supporting PTT Mode and WebSocket Real-time Communication**

[Quick Start](#quick-start) | [Features](#features) | [Live Demo](#live-demo) | [Documentation](#documentation) | [FAQ](#faq)

</div>

---

## 📖 Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Live Demo](#live-demo)
- [Quick Start](#quick-start)
  - [Requirements](#requirements)
  - [One-Click Deployment](#one-click-deployment)
  - [Docker Deployment](#docker-deployment)
  - [Manual Deployment](#manual-deployment)
- [Usage Examples](#usage-examples)
- [API Documentation](#api-documentation)
- [Performance Metrics](#performance-metrics)
- [Technical Architecture](#technical-architecture)
- [Documentation](#documentation)
- [FAQ](#faq)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Introduction

This project is a high-performance real-time speech transcription backend service based on Alibaba DAMO Academy's open-source [FunASR](https://github.com/modelscope/FunASR) engine. It adopts PTT (Push-to-Talk) mode and implements low-latency bidirectional communication through WebSocket protocol, specifically designed for real-time speech recognition scenarios.

### 🎯 Core Advantages

- **🚀 Fast Response**: Model resides in memory, recognition latency < 1000ms (CPU environment)
- **💡 Smart Control**: PTT mode for precise control, on-demand recognition, resource-saving
- **🔧 Easy Deployment**: Pure CPU environment, supports Docker one-click deployment
- **📊 Production Ready**: Supports load balancing, health checks, detailed logging
- **🌐 Standard Protocol**: Based on WebSocket, easy to integrate with various frontends
- **🎨 Out-of-the-Box**: Provides test page for quick functionality verification

---

## Features

### ✨ Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Real-time Speech Recognition** | Based on FunASR paraformer-zh-streaming model | ✅ |
| **PTT Mode** | Supports start/stop/reset control commands | ✅ |
| **WebSocket Communication** | Low-latency bidirectional real-time communication | ✅ |
| **Streaming Processing** | Receive and recognize simultaneously, return results in real-time | ✅ |
| **Multi-user Concurrency** | Supports 10-20 concurrent connections (CPU environment) | ✅ |
| **Model Resident** | Pre-loaded model, no computing resources consumed when idle | ✅ |

### 🔌 API Support

- **WebSocket Interface**: `/ws/asr` - Main speech recognition interface
- **HTTP Interfaces**:
  - `/` - Service information
  - `/health` - Health check
  - `/stats` - Statistics
  - `/test` - Test page

### 📦 Deployment Methods

- ✅ **Direct Deployment**: Python virtual environment, suitable for development and debugging
- ✅ **Docker Deployment**: Containerized deployment, suitable for production
- ✅ **One-Click Deployment**: Windows/Linux scripts, zero-configuration startup

### 🎯 Supported Audio Formats

| Parameter | Value |
|-----------|-------|
| Sample Rate | 16000 Hz |
| Channels | 1 (Mono) |
| Encoding Format | PCM |
| Bit Depth | 16 bit (INT16) |
| Transfer Encoding | Base64 |

---

## Live Demo

After the service starts, visit the test page to experience:

```
http://localhost:9999/test
```

![Test Page Example](./docs/images/demo.png)

> 📝 **Note**: The test page provides complete WebSocket interaction examples, including connection management, control command sending, message receiving, etc.

---

## Quick Start

### Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10+ / Ubuntu 20.04+ / CentOS 7+ | - |
| **Python** | 3.8+ | 3.9+ |
| **CPU** | 2 cores | 4+ cores |
| **Memory** | 4GB | 8GB+ |
| **Disk** | 10GB | 20GB+ |
| **Docker** (Optional) | 20.10+ | Latest |

### One-Click Deployment

#### Windows

```batch
# Right-click "Run as Administrator"
一键部署.bat

# Choose deployment method:
# [1] Direct Deployment - For development
# [2] Docker Deployment - For production
```

#### Linux/macOS

```bash
# Grant execute permission
chmod +x start.sh

# Run startup script
./start.sh
```

After service starts, visit:
- Home: http://localhost:9999
- Test Page: http://localhost:9999/test
- Health Check: http://localhost:9999/health

### Docker Deployment

#### Method 1: Using Docker Compose (Recommended)

```bash
# 1. Clone the project
git clone <repository_url>
cd asr

# 2. Start service
docker-compose up -d

# 3. View logs
docker-compose logs -f

# 4. Stop service
docker-compose down
```

#### Method 2: Using Docker Commands

```bash
# Build image
docker build -t asr-service:latest .

# Run container
docker run -d \
  --name asr-service \
  -p 9999:9999 \
  -v $(pwd)/models:/root/.cache/modelscope \
  -v $(pwd)/logs:/app/logs \
  asr-service:latest

# View logs
docker logs -f asr-service
```

### Manual Deployment

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install PyTorch (CPU version)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Install other dependencies
pip install -r requirements.txt

# 4. Start service
python app.py
```

---

## Usage Examples

### Python Client Example

```python
import asyncio
import websockets
import json
import base64
import numpy as np

async def test_asr():
    uri = "ws://localhost:9999/ws/asr"
    
    async with websockets.connect(uri) as websocket:
        # 1. Receive connection confirmation
        response = await websocket.recv()
        print(f"Connected: {response}")
        
        # 2. Send start command
        await websocket.send(json.dumps({
            "type": "control",
            "command": "start",
            "timestamp": int(time.time() * 1000)
        }))
        
        # 3. Send audio data
        # Assume audio_data is 16kHz, mono, PCM format audio
        audio_base64 = base64.b64encode(audio_data).decode()
        await websocket.send(json.dumps({
            "type": "audio",
            "data": audio_base64,
            "timestamp": int(time.time() * 1000)
        }))
        
        # 4. Receive recognition result
        result = await websocket.recv()
        result_json = json.loads(result)
        print(f"Result: {result_json['text']}")
        
        # 5. Send stop command
        await websocket.send(json.dumps({
            "type": "control",
            "command": "stop",
            "timestamp": int(time.time() * 1000)
        }))

asyncio.run(test_asr())
```

### JavaScript Client Example

```javascript
// Establish WebSocket connection
const ws = new WebSocket('ws://localhost:9999/ws/asr');

ws.onopen = () => {
    console.log('WebSocket connection established');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'result') {
        console.log('Recognition result:', data.text);
    } else if (data.type === 'status') {
        console.log('Status:', data.message);
    }
};

// Send start command
function startRecording() {
    ws.send(JSON.stringify({
        type: 'control',
        command: 'start',
        timestamp: Date.now()
    }));
}

// Send audio data
function sendAudio(audioData) {
    // audioData should be Base64 encoded PCM data
    ws.send(JSON.stringify({
        type: 'audio',
        data: audioData,
        timestamp: Date.now()
    }));
}

// Send stop command
function stopRecording() {
    ws.send(JSON.stringify({
        type: 'control',
        command: 'stop',
        timestamp: Date.now()
    }));
}
```

### cURL Test Health Check

```bash
# Health check
curl http://localhost:9999/health

# Service information
curl http://localhost:9999/

# Statistics
curl http://localhost:9999/stats
```

---

## API Documentation

### WebSocket Protocol

#### Connection URL
```
ws://[server_ip]:9999/ws/asr
```

#### Client → Server

**Control Commands**
```json
{
  "type": "control",
  "command": "start|stop|reset",
  "timestamp": 1698756432000
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Message type, fixed as "control" |
| command | string | Yes | Control command: start / stop / reset |
| timestamp | integer | No | Timestamp (milliseconds) |

**Audio Data**
```json
{
  "type": "audio",
  "data": "base64_encoded_pcm_data",
  "timestamp": 1698756432000
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Message type, fixed as "audio" |
| data | string | Yes | Base64 encoded PCM audio data |
| timestamp | integer | No | Timestamp (milliseconds) |

#### Server → Client

**Recognition Result**
```json
{
  "type": "result",
  "mode": "partial",
  "text": "Recognized text content",
  "timestamp": 1698756432000,
  "confidence": 0.95,
  "processing_time_ms": 125.5
}
```

| Field | Type | Description |
|-------|------|-------------|
| type | string | Message type, fixed as "result" |
| mode | string | Result mode: partial / final |
| text | string | Recognized text content |
| timestamp | integer | Timestamp (milliseconds) |
| confidence | float | Confidence (0-1) |
| processing_time_ms | float | Processing time (milliseconds) |

**Status Message**
```json
{
  "type": "status",
  "code": 200,
  "message": "Connection successful",
  "timestamp": 1698756432000
}
```

**Error Message**
```json
{
  "type": "error",
  "code": 500,
  "message": "Error description",
  "timestamp": 1698756432000
}
```

### HTTP Interfaces

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Service information | JSON |
| `/health` | GET | Health check | JSON |
| `/stats` | GET | Statistics | JSON |
| `/test` | GET | Test page | HTML |

---

## Performance Metrics

### CPU Environment (4 cores / 8GB RAM)

| Metric | Value | Description |
|--------|-------|-------------|
| **Recognition Latency** | < 1000ms | End-to-end latency per recognition |
| **Concurrent Connections** | 10-20 | Simultaneous WebSocket connections |
| **CPU Usage** | 40-60% | CPU usage at full load |
| **Memory Usage** | ~4GB | Memory usage after model loading |
| **Recognition Accuracy** | ≥ 95% | Standard Mandarin environment |

### GPU Environment (Optional)

| Metric | Value | Description |
|--------|-------|-------------|
| **Recognition Latency** | < 300ms | With GPU acceleration |
| **Concurrent Connections** | 50-100 | Concurrency capability in GPU environment |
| **GPU Usage** | 30-50% | GPU usage at full load |

---

## Technical Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (WebSocket Client)                  │
│         Send audio data + control commands (start/stop)       │
└─────────────────────────────────────────────────────────────┘
                          ↓ WebSocket
┌─────────────────────────────────────────────────────────────┐
│               Backend Interface Service (FastAPI)             │
├─────────────────────────────────────────────────────────────┤
│  Web Service Layer                                            │
│  ┌─────────────────────────────────────────┐                │
│  │  FastAPI + WebSocket Handler           │                │
│  │  • Accept WebSocket connections         │                │
│  │  • Route: /ws/asr                       │                │
│  └─────────────────────────────────────────┘                │
│                          ↓                                    │
│  Business Logic Layer                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │Connection  │  │Audio       │  │Result      │            │
│  │Management  │  │Processing  │  │Packaging   │            │
│  │• Multi-conn│  │• Base64    │  │• JSON wrap │            │
│  │• State     │  │  decode    │  │• Timestamp │            │
│  │  tracking  │  │• PCM conv. │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                          ↓                                    │
│  Speech Recognition Layer (FunASR)                            │
│  ┌─────────────────────────────────────────┐                │
│  │   FunASR Model (Resident in Memory)     │                │
│  │   • paraformer-zh-streaming             │                │
│  │   • Loaded at application startup       │                │
│  │   • Called generate() when receiving    │                │
│  │     audio                                │                │
│  │   • Idle when no audio, no computing    │                │
│  │     resources consumed                   │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Programming Language** | Python | 3.8+ |
| **Web Framework** | FastAPI | 0.104+ |
| **WebSocket** | websockets | 12.0+ |
| **ASR Engine** | FunASR | 1.0+ |
| **Deep Learning** | PyTorch | 2.1.0 (CPU) |
| **Audio Processing** | soundfile, numpy | - |
| **Containerization** | Docker, Docker Compose | - |

---

## Documentation

- [📘 Development Documentation](./开发文档.md) - Detailed technical design and implementation (Chinese)
- [📗 Deployment Documentation](./部署文档.md) - Complete deployment guide and operations manual (Chinese)
- [📙 Quick Start Guide](./快速启动指南.md) - Get started in 5 minutes (Chinese)
- [📕 Windows User Guide](./Windows使用说明.md) - Windows platform-specific guide (Chinese)
- [📊 Project Delivery Checklist](./项目交付清单.md) - Feature checklist and verification steps (Chinese)

---

## FAQ

<details>
<summary><b>Q: Model download is slow, what should I do?</b></summary>

A: The model is automatically downloaded from ModelScope. If download is slow, you can:
1. Use a proxy or VPN
2. Manually download the model to `~/.cache/modelscope/` directory
3. Wait for automatic retry

</details>

<details>
<summary><b>Q: How to increase concurrent connections?</b></summary>

A: 
1. Increase server CPU cores
2. Deploy multiple instances + Nginx load balancing
3. Use GPU acceleration (can improve performance by 3-5x)
4. Adjust `MAX_CONNECTIONS` environment variable

</details>

<details>
<summary><b>Q: Support for other languages?</b></summary>

A: Yes! Modify the `MODEL_NAME` environment variable:
- Chinese: `paraformer-zh-streaming`
- English: `paraformer-en-streaming`

</details>

<details>
<summary><b>Q: Docker build fails, what should I do?</b></summary>

A: 
1. Configure Docker mirror accelerator
2. Check network connection
3. View detailed error logs
4. Refer to [Windows User Guide](./Windows使用说明.md) (Chinese)

</details>

<details>
<summary><b>Q: How is the CPU environment performance?</b></summary>

A: 
- Single recognition latency: 500-1000ms
- Concurrent connections: 10-20
- Suitable for small to medium-scale applications
- GPU recommended for better performance

</details>

<details>
<summary><b>Q: How to deploy in production environment?</b></summary>

A: Recommended configuration:
1. Use Docker Compose deployment
2. Configure Nginx reverse proxy
3. Enable HTTPS/WSS
4. Deploy multiple instances + load balancing
5. Configure monitoring and logging

See [Deployment Documentation](./部署文档.md) for details (Chinese)

</details>

---

## Changelog

### v2.1.0 (2024-10-28)

#### Added
- ✨ Windows one-click deployment script
- ✨ Complete testing toolkit
- ✨ Detailed usage documentation

#### Optimized
- 🔧 Optimized for pure CPU deployment solution
- 🔧 Docker image uses Alibaba Cloud sources
- 🔧 Step-by-step PyTorch installation to avoid version conflicts
- 🔧 All scripts automatically switch to correct directory

#### Fixed
- 🐛 Fixed Docker deployment path issues
- 🐛 Fixed batch script directory switching issues

### v2.0.0 (2024-10-28)

- 🎉 First release
- ✨ PTT mode support
- ✨ WebSocket real-time communication
- ✨ Docker deployment support

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Code Style: Follow PEP 8
- Commit Messages: Use semantic commit conventions
- Testing: Add necessary unit tests
- Documentation: Update relevant documentation

---

## Acknowledgments

This project is based on the following excellent open-source projects:

- [FunASR](https://github.com/modelscope/FunASR) - Alibaba DAMO Academy's open-source speech recognition toolkit
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [ModelScope](https://www.modelscope.cn/) - Model hosting platform

Thanks to all contributors for their support!

---

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details

---

<div align="center">

**If this project helps you, please give it a ⭐️ Star!**

Made with ❤️ by Hurrvey

</div>

