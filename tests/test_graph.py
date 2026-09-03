import unittest
from platium.scanners.graph.scanner import search

class TestGraphScanner(unittest.TestCase):
    def test_valid_email(self):
        result = search("test@example.com")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "test@example.com")
        self.assertIn("connections", result)

    def test_empty_email(self):
        result = search("")
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
