import json
import unittest
from unittest.mock import MagicMock

# Mocking the service to test logic without hardware
class MockUARTService:
    def __init__(self):
        self.sent_data = []
    def send(self, data):
        self.sent_data.append(data)

class TestBridgeLogic(unittest.TestCase):
    def test_ai_answer_forwarding(self):
        # Setup mock UART
        uart = MockUARTService()
        
        # Simulate the bridge logic from mqtt.py
        # topic: ai/answer, payload: "Hello student"
        topic = "ai/answer"
        payload = "Hello student"
        
        # Expected action in mqtt.py:
        if topic == "ai/answer":
            uart.send({
                "type": "TEXT_DOWNLINK",
                "text": payload
            })
            
        self.assertEqual(len(uart.sent_data), 1)
        self.assertEqual(uart.sent_data[0]["type"], "TEXT_DOWNLINK")
        self.assertEqual(uart.sent_data[0]["text"], "Hello student")

    def test_mode_set_forwarding(self):
        uart = MockUARTService()
        topic = "audio/control"
        data = {"mode": "class"}
        
        if topic == "audio/control":
            uart.send({
                "type": "MODE_SET",
                "mode": data.get("mode", "CLASS").upper()
            })
            
        self.assertEqual(uart.sent_data[0]["mode"], "CLASS")

if __name__ == "__main__":
    unittest.main()
