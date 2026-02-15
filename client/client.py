"""
Client library for interacting with the line sampler server.
"""
import socket
import logging
from typing import List, Optional
from server.protocol import Protocol, SOCKET_PATH, MAX_MESSAGE_SIZE

logger = logging.getLogger(__name__)

class LineClient:
    """
    Client for the line sampling service.
    
    Usage:
        client = LineClient()
        lines_read = client.load("path/to/file.txt")
        samples = client.sample(10)
    """
    
    def __init__(self, socket_path: str = SOCKET_PATH):
        """
        Initialize client.
        
        Args:
            socket_path: Path to server socket
        """
        self.socket_path = socket_path
        self._connect()
    
    def _connect(self):
        """Establish connection to server."""
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(self.socket_path)
    
    def _send_request(self, method: str, params: dict) -> dict:
        """
        Send request and receive response.
        
        Args:
            method: Method name
            params: Parameters
            
        Returns:
            Response dictionary
            
        Raises:
            Exception: If server returns error
        """
        # Send request
        request = Protocol.encode_request(method, params)
        self.socket.sendall(request)
        
        # Receive response
        response_data = self.socket.recv(MAX_MESSAGE_SIZE)
        response = Protocol.decode(response_data)
        
        if response.get("error"):
            raise Exception(response["error"])
        
        return response.get("result", {})
    
    def load(self, file_path: str) -> int:
        """
        Load lines from a file into the server cache.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Number of lines read
        """
        result = self._send_request("load", {"file_path": file_path})
        return result.get("lines_read", 0)
    
    def sample(self, n: int) -> List[str]:
        """
        Sample n random lines from the cache.
        
        Args:
            n: Number of lines to sample
            
        Returns:
            List of sampled lines
        """
        result = self._send_request("sample", {"n": n})
        return result.get("lines", [])
    
    def close(self):
        """Close the client connection."""
        if hasattr(self, 'socket'):
            self.socket.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()