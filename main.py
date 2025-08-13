import asyncio
import json
import traceback

import websockets
from websockets.server import WebSocketServerProtocol

import action
import perception

# 简单的日志记录
def log(message: str):
    print(f"[Main] {message}")

# 将我们的工具函数映射到一个字典中，方便调用
TOOL_MAP = {
    "state_tool": perception.get_ui_state,
    "click_tool": action.click_tool,
    "type_tool": action.type_tool,
    "key_tool": action.key_tool,
}

async def handler(websocket: WebSocketServerProtocol, path: str):
    """处理单个 WebSocket 连接。"""
    log(f"Client connected from {websocket.remote_address}")

    # 1. 发送注册消息，表明自己的身份
    registration_msg = {
        "event_type": "meta.linux_mcp.lifecycle.connect",
        "content": [
            {
                "type": "meta.lifecycle",
                "data": {
                    "details": {
                        "display_name": "Linux 操作平台 (小脑 PoC)"
                    }
                }
            }
        ]
    }
    await websocket.send(json.dumps(registration_msg))
    log("Registration message sent.")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                log(f"Received message: {data}")

                request_id = data.get("event_id")
                content = data.get("content", [])
                if not request_id or not content or content[0].get("type") != "action_params":
                    continue

                action_params_data = content[0].get("data", {})
                event_type_parts = data.get("event_type", "").split('.')

                if len(event_type_parts) < 3:
                    continue

                method = event_type_parts[2] # e.g., action.linux_mcp.click_tool -> click_tool

                if method in TOOL_MAP:
                    tool_func = TOOL_MAP[method]

                    # 执行工具函数
                    # 注意：state_tool 没有参数，其他有
                    if method == "state_tool":
                        result = tool_func()
                    else:
                        result = tool_func(**action_params_data)

                    response = {
                        "event_type": f"action_response.linux_mcp.{method}.success",
                        "content": [
                            {
                                "type": f"action_response.{method}",
                                "data": {
                                    "original_event_id": request_id,
                                    "status": "success",
                                    "data": result,
                                }
                            }
                        ]
                    }
                else:
                    response = {
                        "event_type": f"action_response.linux_mcp.{method}.error",
                        "content": [
                            {
                                "type": f"action_response.{method}",
                                "data": {
                                    "original_event_id": request_id,
                                    "status": "error",
                                    "message": f"Unknown method: {method}",
                                }
                            }
                        ]
                    }

                await websocket.send(json.dumps(response))
                log(f"Sent response for request {request_id}")

            except json.JSONDecodeError:
                log(f"Error: Received non-JSON message: {message}")
            except Exception as e:
                log(f"Error processing message: {e}\n{traceback.format_exc()}")

    except websockets.exceptions.ConnectionClosed:
        log(f"Client disconnected from {websocket.remote_address}")
    finally:
        log("Connection handler finished.")


async def main():
    """启动 WebSocket 服务器。"""
    host = "0.0.0.0"
    port = 8078 # 使用一个与 Core 不同的端口
    log(f"Starting Linux-MCP WebSocket server on ws://{host}:{port}")
    async with websockets.serve(handler, host, port, max_size=50 * 1024 * 1024):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped by user.")