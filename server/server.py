"""
Main server implementation using Unix domain sockets.
Handles multiple concurrent clients with threading.
"""
import os
import socket
import threading
import logging
from server.cache_manager import ThreadSafeCache
from server.protocol import Protocol, SOCKET_PATH, MAX_MESSAGE_SIZE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LineServer:
    """
    Threaded server for line sampling service.
    
    Provides:
    - load(file_path): Load lines from file into cache
    - sample(n): Randomly sample n lines from cache
    """
    
    def __init__(self, socket_path: str = SOCKET_PATH):
        """
        Initialize server.
        
        Args:
            socket_path: Path for Unix domain socket
        """
        self.socket_path = socket_path
        self.cache = ThreadSafeCache()
        self.server_socket = None
        self.running = False
        self.threads = []
        
    def start(self):
        """Start the server."""
        # Remove old socket if exists
        try:
            os.unlink(self.socket_path)
        except OSError:
            if os.path.exists(self.socket_path):
                raise
        
        # Create socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(5)  # Allow up to 5 pending connections
        self.running = True
        
        logger.info(f"Server started on {self.socket_path}")
        
        # Main accept loop
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                # Handle each client in a new thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                self.threads.append(client_thread)
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket: socket.socket):
        """
        Handle a single client connection.
        
        Args:
            client_socket: Socket connected to client
        """
        logger.info(f"New client connected")
        
        try:
            while True:
                # Receive message
                data = client_socket.recv(MAX_MESSAGE_SIZE)
                if not data:
                    break
                
                # Parse request
                try:
                    message = Protocol.decode(data)
                    if message.get("type") != "request":
                        raise ValueError("Invalid message type")
                    
                    method = message.get("method")
                    params = message.get("params", {})
                    
                    # Process request
                    if method == "load":
                        result = self.handle_load(params)
                    elif method == "sample":
                        result = self.handle_sample(params)
                    else:
                        raise ValueError(f"Unknown method: {method}")
                    
                    # Send response
                    response = Protocol.encode_response(result)
                    client_socket.sendall(response)
                    
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    response = Protocol.encode_response(None, str(e))
                    client_socket.sendall(response)
        
        except Exception as e:
            logger.error(f"Client connection error: {e}")
        finally:
            client_socket.close()
            logger.info("Client disconnected")
    
    def handle_load(self, params: dict) -> dict:
        """
        Handle load request.
        
        Args:
            params: Must contain 'file_path'
            
        Returns:
            Dictionary with 'lines_read' count
        """
        file_path = params.get("file_path")
        if not file_path:
            raise ValueError("Missing file_path parameter")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Strip newlines but keep empty lines
                lines = [line.rstrip('\n\r') for line in lines]
            
            count = self.cache.add_lines(lines)
            return {"lines_read": count}
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
    
    def handle_sample(self, params: dict) -> dict:
        """
        Handle sample request.
        
        Args:
            params: Must contain 'n' (number of lines to sample)
            
        Returns:
            Dictionary with 'lines' list
        """
        n = params.get("n")
        if n is None:
            raise ValueError("Missing n parameter")
        
        try:
            n = int(n)
            if n < 0:
                raise ValueError("n must be non-negative")
        except ValueError:
            raise ValueError("n must be an integer")
        
        lines = self.cache.sample(n)
        return {"lines": lines}
    
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Clean up socket file
        try:
            os.unlink(self.socket_path)
        except OSError:
            pass
        
        logger.info("Server stopped")
    
    def get_stats(self) -> dict:
        """Get server statistics."""
        return self.cache.get_stats()

def run_server():
    """Run the server (blocking)."""
    server = LineServer()
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        server.stop()

if __name__ == "__main__":
    run_server()