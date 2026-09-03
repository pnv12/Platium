import unittest
from platium.scanners.graph.scanner import search

class TestGraphScanner(unittest.TestCase):
    def test_empty_graph(self):
        result = search("testuser")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "testuser")
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["nodes"], [])
        self.assertEqual(result["edges"], [])

    def test_graph_with_no_data(self):
        result = search("nonexistent")
        self.assertEqual(result["status"], "empty")
        self.assertIn("nodes", result)
        self.assertIn("edges", result)

if __name__ == "__main__":
    unittest.main()
