import asyncio
import websockets
import json
import base64
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

class WebSocketHandler:
    """WebSocket handler for ESP32 devices - Xiaozhi protocol compatible"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.connected_devices: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.server = None
        
    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection from ESP32 device"""
        device_id = None
        remote_addr = websocket.remote_address
        
        try:
            logger.info(f"[WebSocket] New connection from {remote_addr}")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'register':
                        device_id = data.get('device_id', f'device_{remote_addr[1]}')
                        self.connected_devices[device_id] = websocket
                        logger.info(f"[WebSocket] Device registered: {device_id}")
                        
                        # Send acknowledgment
                        await websocket.send(json.dumps({
                            'type': 'register_ack',
                            'device_id': device_id,
                            'status': 'connected'
                        }))
                        
                    elif msg_type == 'audio':
                        if not device_id:
                            logger.warning("[WebSocket] Audio received before registration")
                            continue
                            
                        # Decode audio data
                        audio_b64 = data.get('audio', '')
                        audio_data = base64.b64decode(audio_b64)
                        flags = data.get('flags', 0)
                        sequence = data.get('sequence', 0)
                        
                        # Process with existing AI service
                        await self.ai_service.process_audio_websocket(
                            device_id, audio_data, flags, sequence, websocket
                        )
                        
                    elif msg_type == 'heartbeat':
                        await websocket.send(json.dumps({
                            'type': 'heartbeat_ack',
                            'timestamp': data.get('timestamp')
                        }))
                    
                    elif msg_type == 'question':
                        # Handle text question from web dashboard
                        question_text = data.get('text', '').strip()
                        if not question_text:
                            logger.warning("[WebSocket] Empty question received")
                            continue
                        
                        logger.info(f"[WebSocket] Text question from {device_id or remote_addr}: {question_text}")
                        
                        # Process with AI
                        try:
                            answer = await self.ai_service.process_text_question(question_text)
                            
                            # Send response
                            await websocket.send(json.dumps({
                                'type': 'answer',
                                'text': answer,
                                'timestamp': data.get('timestamp')
                            }))
                            
                            logger.info(f"[WebSocket] Sent answer: {answer[:100]}...")
                            
                        except Exception as e:
                            logger.error(f"[WebSocket] Error processing question: {e}")
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': 'Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi'
                            }))
                        
                    else:
                        logger.warning(f"[WebSocket] Unknown message type: {msg_type}")

                        
                except json.JSONDecodeError:
                    logger.error(f"[WebSocket] Invalid JSON from {device_id or remote_addr}")
                except Exception as e:
                    logger.error(f"[WebSocket] Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[WebSocket] Connection closed: {device_id or remote_addr}")
        finally:
            if device_id and device_id in self.connected_devices:
                del self.connected_devices[device_id]
                logger.info(f"[WebSocket] Device removed: {device_id}")
    
    async def send_response(self, device_id: str, text: str, has_visual: bool = False, visual_type: str = None, visual_param: str = None):
        """Send AI response to device via WebSocket"""
        if device_id not in self.connected_devices:
            logger.warning(f"[WebSocket] Device {device_id} not connected, cannot send response")
            return False
            
        try:
            websocket = self.connected_devices[device_id]
            response = {
                'type': 'ai_response',
                'text': text,
                'has_visual': has_visual
            }
            
            if has_visual:
                response['visual_type'] = visual_type
                response['visual_param'] = visual_param
                
            await websocket.send(json.dumps(response))
            logger.info(f"[WebSocket] Sent response to {device_id}: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"[WebSocket] Error sending response to {device_id}: {e}")
            return False
    
    async def send_text_chunk(self, device_id: str, text_chunk: str, is_final: bool = False):
        """Send streaming text chunk to device"""
        if device_id not in self.connected_devices:
            return False
            
        try:
            websocket = self.connected_devices[device_id]
            await websocket.send(json.dumps({
                'type': 'text_chunk',
                'text': text_chunk,
                'is_final': is_final
            }))
            return True
        except Exception as e:
            logger.error(f"[WebSocket] Error sending chunk to {device_id}: {e}")
            return False
    
    async def broadcast(self, message_type: str, data: dict):
        """Broadcast message to all connected devices"""
        disconnected = []
        
        for device_id, websocket in self.connected_devices.items():
            try:
                await websocket.send(json.dumps({
                    'type': message_type,
                    **data
                }))
            except Exception as e:
                logger.error(f"[WebSocket] Error broadcasting to {device_id}: {e}")
                disconnected.append(device_id)
        
        # Clean up disconnected devices
        for device_id in disconnected:
            del self.connected_devices[device_id]
    
    async def start_server(self, host: str = '0.0.0.0', port: int = 8765):
        """Start WebSocket server"""
        self.server = await websockets.serve(
            self.handle_connection,
            host,
            port,
            ping_interval=20,
            ping_timeout=10
        )
        logger.info(f"🔌 WebSocket server started on {host}:{port}")
        return self.server
    
    async def stop_server(self):
        """Stop WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("[WebSocket] Server stopped")
    
    def get_connected_devices(self) -> Set[str]:
        """Get list of connected device IDs"""
        return set(self.connected_devices.keys())
    
    def is_device_connected(self, device_id: str) -> bool:
        """Check if device is connected"""
        return device_id in self.connected_devices
