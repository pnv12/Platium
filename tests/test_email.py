import unittest
from platium.scanners.email.scanner import search

class TestEmailScanner(unittest.TestCase):
    def test_valid_email(self):
        result = search("test@example.com")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "test@example.com")
        self.assertIn("sources", result)

    def test_invalid_email(self):
        # Просто перевіряємо, що функція не падає
        result = search("invalid")
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
