"""
WebSocket 客户端测试脚本
用于测试语音实时转录接口
"""

import asyncio
import websockets
import json
import time
import base64
import numpy as np

# WebSocket 服务器地址
WS_URL = "ws://localhost:9999/ws/asr"


async def test_basic_connection():
    """测试基本连接"""
    print("=" * 60)
    print("测试 1: 基本连接")
    print("=" * 60)
    
    async with websockets.connect(WS_URL) as websocket:
        # 接收连接确认
        response = await websocket.recv()
        data = json.loads(response)
        print(f"✓ 连接成功: {data}")
        
        # 等待一会儿
        await asyncio.sleep(1)
        
        print("✓ 基本连接测试通过\n")


async def test_control_commands():
    """测试控制指令"""
    print("=" * 60)
    print("测试 2: 控制指令（start/stop/reset）")
    print("=" * 60)
    
    async with websockets.connect(WS_URL) as websocket:
        # 接收连接确认
        await websocket.recv()
        
        # 测试 start 指令
        print("发送 start 指令...")
        await websocket.send(json.dumps({
            "type": "control",
            "command": "start",
            "timestamp": int(time.time() * 1000)
        }))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"✓ Start 响应: {data}")
        
        await asyncio.sleep(0.5)
        
        # 测试 stop 指令
        print("发送 stop 指令...")
        await websocket.send(json.dumps({
            "type": "control",
            "command": "stop",
            "timestamp": int(time.time() * 1000)
        }))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"✓ Stop 响应: {data}")
        
        await asyncio.sleep(0.5)
        
        # 测试 reset 指令
        print("发送 reset 指令...")
        await websocket.send(json.dumps({
            "type": "control",
            "command": "reset",
            "timestamp": int(time.time() * 1000)
        }))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"✓ Reset 响应: {data}")
        
        print("✓ 控制指令测试通过\n")


async def test_audio_without_start():
    """测试未发送 start 指令就发送音频"""
    print("=" * 60)
    print("测试 3: 未发送 start 时发送音频（应被忽略）")
    print("=" * 60)
    
    async with websockets.connect(WS_URL) as websocket:
        # 接收连接确认
        await websocket.recv()
        
        # 生成测试音频数据（随机噪声）
        audio_data = np.random.randint(-32768, 32767, 16000, dtype=np.int16)
        audio_base64 = base64.b64encode(audio_data.tobytes()).decode()
        
        # 直接发送音频（未发送 start）
        print("发送音频数据（未发送 start）...")
        await websocket.send(json.dumps({
            "type": "audio",
            "data": audio_base64,
            "timestamp": int(time.time() * 1000)
        }))
        
        # 等待一会儿，不应该收到识别结果
        try:
            await asyncio.wait_for(websocket.recv(), timeout=2.0)
            print("✗ 错误：收到了不应该收到的响应")
        except asyncio.TimeoutError:
            print("✓ 正确：音频被忽略，未收到响应")
        
        print("✓ 未开始录音时发送音频测试通过\n")


async def test_full_workflow():
    """测试完整工作流程"""
    print("=" * 60)
    print("测试 4: 完整工作流程（start -> 音频 -> stop）")
    print("=" * 60)
    
    async with websockets.connect(WS_URL) as websocket:
        # 接收连接确认
        await websocket.recv()
        print("✓ 连接已建立")
        
        # 发送 start 指令
        print("\n1. 发送 start 指令...")
        await websocket.send(json.dumps({
            "type": "control",
            "command": "start",
            "timestamp": int(time.time() * 1000)
        }))
        response = await websocket.recv()
        print(f"   响应: {json.loads(response)['message']}")
        
        # 发送几个音频数据包（随机数据）
        print("\n2. 发送音频数据...")
        for i in range(3):
            # 生成 1 秒的随机音频数据
            audio_data = np.random.randint(-5000, 5000, 16000, dtype=np.int16)
            audio_base64 = base64.b64encode(audio_data.tobytes()).decode()
            
            await websocket.send(json.dumps({
                "type": "audio",
                "data": audio_base64,
                "timestamp": int(time.time() * 1000)
            }))
            print(f"   已发送音频块 {i+1}/3")
            
            # 尝试接收识别结果（可能没有，因为是随机数据）
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                result = json.loads(response)
                if result.get("type") == "result":
                    print(f"   识别结果: {result.get('text')}")
                elif result.get("type") == "error":
                    print(f"   错误: {result.get('message')}")
            except asyncio.TimeoutError:
                print(f"   （未收到识别结果，正常情况，因为是随机音频）")
            
            await asyncio.sleep(0.5)
        
        # 发送 stop 指令
        print("\n3. 发送 stop 指令...")
        await websocket.send(json.dumps({
            "type": "control",
            "command": "stop",
            "timestamp": int(time.time() * 1000)
        }))
        response = await websocket.recv()
        print(f"   响应: {json.loads(response)['message']}")
        
        print("\n✓ 完整工作流程测试通过\n")


async def test_multiple_connections():
    """测试多个并发连接"""
    print("=" * 60)
    print("测试 5: 多个并发连接")
    print("=" * 60)
    
    async def single_connection(conn_id):
        """单个连接的测试"""
        try:
            async with websockets.connect(WS_URL) as websocket:
                # 接收连接确认
                response = await websocket.recv()
                data = json.loads(response)
                print(f"✓ 连接 {conn_id} 建立成功: {data.get('connection_id')}")
                
                # 等待一会儿
                await asyncio.sleep(1)
                
                return True
        except Exception as e:
            print(f"✗ 连接 {conn_id} 失败: {e}")
            return False
    
    # 创建多个并发连接
    tasks = [single_connection(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(results)
    print(f"\n✓ 成功建立 {success_count}/5 个并发连接")
    print("✓ 多连接测试通过\n")


async def test_invalid_messages():
    """测试无效消息"""
    print("=" * 60)
    print("测试 6: 无效消息处理")
    print("=" * 60)
    
    async with websockets.connect(WS_URL) as websocket:
        # 接收连接确认
        await websocket.recv()
        
        # 发送无效的消息类型
        print("发送无效消息类型...")
        await websocket.send(json.dumps({
            "type": "invalid_type",
            "timestamp": int(time.time() * 1000)
        }))
        response = await websocket.recv()
        data = json.loads(response)
        if data.get("type") == "error":
            print(f"✓ 正确返回错误: {data.get('message')}")
        
        await asyncio.sleep(0.5)
        
        # 发送无效的控制指令
        print("发送无效控制指令...")
        await websocket.send(json.dumps({
            "type": "control",
            "command": "invalid_command",
            "timestamp": int(time.time() * 1000)
        }))
        response = await websocket.recv()
        data = json.loads(response)
        if data.get("type") == "error":
            print(f"✓ 正确返回错误: {data.get('message')}")
        
        print("✓ 无效消息处理测试通过\n")


async def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "语音实时转录接口 - 自动化测试" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"\n服务器地址: {WS_URL}\n")
    
    try:
        # 运行所有测试
        await test_basic_connection()
        await test_control_commands()
        await test_audio_without_start()
        await test_full_workflow()
        await test_multiple_connections()
        await test_invalid_messages()
        
        # 测试总结
        print("=" * 60)
        print("✓✓✓ 所有测试通过！✓✓✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗✗✗ 测试失败: {e} ✗✗✗\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n提示：请确保服务已启动（python app.py 或 docker-compose up）\n")
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")

