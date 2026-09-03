import unittest
from platium.scanners.phone.scanner import search

class TestPhoneScanner(unittest.TestCase):
    def test_valid_phone(self):
        result = search("+380991234567")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "+380991234567")
        self.assertEqual(result["status"], "valid")
        self.assertIn("data", result)
        self.assertIn("country", result["data"])

    def test_invalid_phone(self):
        result = search("invalid")
        self.assertEqual(result["status"], "invalid")
        self.assertIn("error", result)

    def test_empty_phone(self):
        result = search("")
        self.assertEqual(result["status"], "invalid")

if __name__ == "__main__":
    unittest.main()
