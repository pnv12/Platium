import unittest
from platium.scanners.threat.scanner import search

class TestThreatScanner(unittest.TestCase):
    def test_valid_ip(self):
        result = search("8.8.8.8")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "8.8.8.8")
        self.assertIn("sources", result)
        self.assertIn("status", result)

    def test_empty_target(self):
        result = search("")
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

if __name__ == "__main__":
    unittest.main()
