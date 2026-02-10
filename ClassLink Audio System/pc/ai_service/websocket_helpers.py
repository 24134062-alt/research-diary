"""
WebSocket processing helpers for AIService
"""
import asyncio
import logging
import time
import json

logger = logging.getLogger(__name__)

async def process_question_websocket(self, audio_bytes: bytes, device_id: str):
    """
    Process question from WebSocket client.
    Similar to process_question but sends response via WebSocket.
    """
    start_time = time.time()
    
    try:
        # Convert PCM to WAV
        wav_data = self.pcm_to_wav(audio_bytes, 16000, 1, 2)
        
        # STT
        loop = asyncio.get_event_loop()
        audio_source = __import__('speech_recognition').AudioFile(__import__('io').BytesIO(wav_data))
        with audio_source as source:
            audio = self.recognizer.record(source)
        
        # Google STT
        raw_text = await loop.run_in_executor(
            self.executor,
            self.recognizer.recognize_google,
            audio,
            'vi-VN'
        )
        
        # Apply subject mode formatting
        processed_text = self.normalize_text_by_mode(raw_text)
        logger.info(f"[{device_id}] Question ({self.current_subject}): {processed_text}")
        
        # Ask AI
        answer_data = await loop.run_in_executor(
            self.executor,
            self.ai_assistant.ask_question_with_visual,
            processed_text,
            device_id
        )
        
        answer_text = answer_data['text']
        has_visual = answer_data['has_visual']
        visual_type = answer_data.get('visual_type')
        visual_param = answer_data.get('visual_param')
        
        logger.info(f"[{device_id}] Answer: {answer_text}")
        if has_visual:
            logger.info(f"[{device_id}] Visual: {visual_type}/{visual_param}")
        
        # Send via WebSocket
        await self.websocket_handler.send_response(
            device_id,
            answer_text,
            has_visual=has_visual,
            visual_type=visual_type,
            visual_param=visual_param
        )
        
        # Also publish to MQTT for logging
        log_payload = {
            "student": device_id,
            "question": processed_text,
            "answer": answer_text
        }
        if self.mqtt_connected:
            self.mqtt_client.publish("student/query/log", json.dumps(log_payload))
        
        elapsed = time.time() - start_time
        logger.info(f"[{device_id}] Completed in {elapsed:.2f}s")
        
    except __import__('speech_recognition').UnknownValueError:
        logger.warning(f"[{device_id}] Could not understand audio")
        await self.websocket_handler.send_response(device_id, "Xin lỗi, em nói lại được không?")
    except Exception as e:
        logger.error(f"[{device_id}] Error processing question: {e}")
        await self.websocket_handler.send_response(device_id, "Xin lỗi, có lỗi xảy ra")
    finally:
        # Remove from active requests
        self.active_requests.pop(device_id, None)


async def process_audio_websocket_wrapper(self, device_id: str, audio_data: bytes, flags: int, sequence: int, websocket):
    """
    Process audio packet from WebSocket connection.
    """
    ai_mode = (flags & 0x01) != 0
    
    if not ai_mode:
        return
    
    # Buffer audio
    if device_id not in self.audio_buffers:
        self.audio_buffers[device_id] = bytearray()
    
    self.audio_buffers[device_id].extend(audio_data)
    
    # End detection: buffer > 3 seconds
    if len(self.audio_buffers[device_id]) > 96000:
        # Check capacity
        if len(self.active_requests) >= self.max_concurrent:
            logger.warning(f"At capacity, {device_id} must wait")
            await self.websocket_handler.send_response(
                device_id,
                "Hệ thống đang bận. Xin chờ 10 giây"
            )
            self.audio_buffers[device_id] = bytearray()
            return
        
        # Process
        audio_copy = bytes(self.audio_buffers[device_id])
        self.audio_buffers[device_id] = bytearray()
        
        task = asyncio.create_task(
            process_question_websocket(self, audio_copy, device_id)
        )
        self.active_requests[device_id] = task
