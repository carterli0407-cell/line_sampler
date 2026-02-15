"""
Integration tests for LineServer.
"""
import unittest
import threading
import tempfile
import os
import time
from server.server import LineServer
from client.client import LineClient

class TestLineServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start server in background thread."""
        cls.server = LineServer("/tmp/test_sampler.sock")
        cls.server_thread = threading.Thread(target=cls.server.start)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.5)  # Give server time to start
    
    @classmethod
    def tearDownClass(cls):
        """Stop server."""
        cls.server.stop()
    
    def setUp(self):
        """Create test data file."""
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.test_lines = [f"Line {i}" for i in range(100)]
        self.test_file.write('\n'.join(self.test_lines))
        self.test_file.close()
    
    def tearDown(self):
        """Clean up test file."""
        os.unlink(self.test_file.name)
    
    def test_load_and_sample(self):
        with LineClient("/tmp/test_sampler.sock") as client:
            # Load file
            count = client.load(self.test_file.name)
            self.assertEqual(count, 100)
            
            # Sample lines
            sampled = client.sample(10)
            self.assertEqual(len(sampled), 10)
            
            # Verify sampled lines are from original set
            for line in sampled:
                self.assertIn(line, self.test_lines)
    
    def test_sample_invalidation(self):
        with LineClient("/tmp/test_sampler.sock") as client:
            client.load(self.test_file.name)
            
            # First client samples 50 lines
            sampled1 = client.sample(50)
            self.assertEqual(len(sampled1), 50)
            
            # Second client should get remaining 50
            with LineClient("/tmp/test_sampler.sock") as client2:
                sampled2 = client2.sample(50)
                self.assertEqual(len(sampled2), 50)
                
                # No overlap between samples
                overlap = set(sampled1) & set(sampled2)
                self.assertEqual(len(overlap), 0)
    
    def test_concurrent_clients(self):
        """Test multiple clients accessing simultaneously."""
        def client_work():
            with LineClient("/tmp/test_sampler.sock") as client:
                client.load(self.test_file.name)
                sampled = client.sample(20)
                self.assertTrue(len(sampled) <= 20)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=client_work)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

if __name__ == "__main__":
    unittest.main()