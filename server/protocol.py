"""
Protocol definitions for client-server communication.
Uses JSON for message serialization.
"""
import json
from typing import Dict, Any, Optional

# Socket path for Unix domain socket
SOCKET_PATH = "/tmp/line_sampler.sock"
# Maximum message size (10MB)
MAX_MESSAGE_SIZE = 10 * 1024 * 1024

class MessageType:
    """Message type constants."""
    LOAD = "load"
    SAMPLE = "sample"
    RESPONSE = "response"
    ERROR = "error"

class Protocol:
    """Handles message encoding/decoding."""
    
    @staticmethod
    def encode_request(method: str, params: Dict[str, Any]) -> bytes:
        """
        Encode a request message.
        
        Args:
            method: Method name ('load' or 'sample')
            params: Method parameters
            
        Returns:
            JSON-encoded bytes
        """
        message = {
            "type": "request",
            "method": method,
            "params": params
        }
        return json.dumps(message).encode('utf-8')
    
    @staticmethod
    def encode_response(result: Any, error: Optional[str] = None) -> bytes:
        """
        Encode a response message.
        
        Args:
            result: Success result
            error: Error message if any
            
        Returns:
            JSON-encoded bytes
        """
        message = {
            "type": "response",
            "result": result,
            "error": error
        }
        return json.dumps(message).encode('utf-8')
    
    @staticmethod
    def decode(data: bytes) -> Dict[str, Any]:
        """
        Decode a message from bytes.
        
        Args:
            data: JSON-encoded bytes
            
        Returns:
            Decoded dictionary
        """
        return json.loads(data.decode('utf-8'))