import unittest
from platium.scanners.ip.scanner import search

class TestIPScanner(unittest.TestCase):
    def test_valid_ip(self):
        result = search("8.8.8.8")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "8.8.8.8")
        self.assertIn("location", result)
        self.assertIn("country", result["location"])

    def test_invalid_ip(self):
        result = search("invalid")
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
