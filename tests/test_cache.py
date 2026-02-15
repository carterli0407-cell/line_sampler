"""
Unit tests for ThreadSafeCache.
"""
import unittest
import threading
from server.cache_manager import ThreadSafeCache

class TestThreadSafeCache(unittest.TestCase):
    def setUp(self):
        self.cache = ThreadSafeCache()
    
    def test_add_lines(self):
        lines = ["line1", "line2", "line3"]
        count = self.cache.add_lines(lines)
        self.assertEqual(count, 3)
        self.assertEqual(self.cache.size(), 3)
    
    def test_sample_basic(self):
        lines = ["line1", "line2", "line3", "line4", "line5"]
        self.cache.add_lines(lines)
        
        sampled = self.cache.sample(3)
        self.assertEqual(len(sampled), 3)
        self.assertEqual(self.cache.size(), 2)
        
        # Verify sampled lines are removed
        remaining = self.cache.sample(5)
        self.assertEqual(len(remaining), 2)
    
    def test_sample_no_replacement(self):
        lines = ["line1", "line2", "line3"]
        self.cache.add_lines(lines)
        
        sampled1 = self.cache.sample(2)
        sampled2 = self.cache.sample(2)
        
        # First sample should have removed 2 lines
        self.assertEqual(len(sampled1), 2)
        self.assertEqual(len(sampled2), 1)
        
        # No duplicates between samples
        all_sampled = set(sampled1) | set(sampled2)
        self.assertEqual(len(all_sampled), 3)
    
    def test_sample_more_than_available(self):
        lines = ["line1", "line2"]
        self.cache.add_lines(lines)
        
        sampled = self.cache.sample(5)
        self.assertEqual(len(sampled), 2)
        self.assertEqual(self.cache.size(), 0)
    
    def test_sample_empty_cache(self):
        sampled = self.cache.sample(3)
        self.assertEqual(len(sampled), 0)
    
    def test_thread_safety(self):
        """Test concurrent access to cache."""
        lines = [f"line{i}" for i in range(1000)]
        self.cache.add_lines(lines)
        
        def sampler(n):
            for _ in range(10):
                self.cache.sample(n)
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=sampler, args=(10,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All lines should be sampled
        stats = self.cache.get_stats()
        self.assertEqual(stats["available_lines"], 0)
        self.assertEqual(stats["total_lines_loaded"], 1000)

if __name__ == "__main__":
    unittest.main()