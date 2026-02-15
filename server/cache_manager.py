"""
Thread-safe cache manager for storing and sampling lines from text files.
Lines are stored and can be randomly sampled without replacement.
"""
import threading
import random
from collections import deque
from typing import List

class ThreadSafeCache:
    """
    Manages a thread-safe collection of text lines.
    
    Features:
    - Add lines to cache
    - Randomly sample lines without replacement
    - Thread-safe operations using locks
    """
    
    def __init__(self):
        """Initialize empty cache with thread lock."""
        self.available_lines = deque()  # Fast O(1) pops from both ends
        self.lock = threading.Lock()
        self.total_lines_loaded = 0
    
    def add_lines(self, lines: List[str]) -> int:
        """
        Add multiple lines to the cache.
        
        Args:
            lines: List of lines to add
            
        Returns:
            Number of lines added
        """
        with self.lock:
            self.available_lines.extend(lines)
            self.total_lines_loaded += len(lines)
            return len(lines)
    
    def sample(self, n: int) -> List[str]:
        """
        Randomly sample n lines from cache without replacement.
        Sampled lines are removed from available cache.
        
        Args:
            n: Number of lines to sample
            
        Returns:
            List of sampled lines (empty if cache is empty)
        """
        with self.lock:
            if not self.available_lines or n <= 0:
                return []
            
            # Can't sample more than available
            n = min(n, len(self.available_lines))
            
            # Random sampling without replacement
            # Convert to list for random.sample, then rebuild deque
            lines_list = list(self.available_lines)
            sampled = random.sample(lines_list, n)
            
            # Rebuild available lines (excluding sampled ones)
            sampled_set = set(sampled)
            self.available_lines = deque(
                [line for line in lines_list if line not in sampled_set]
            )
            
            return sampled
    
    def size(self) -> int:
        """Get current number of available lines."""
        with self.lock:
            return len(self.available_lines)
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self.lock:
            return {
                "available_lines": len(self.available_lines),
                "total_lines_loaded": self.total_lines_loaded
            }