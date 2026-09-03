import unittest
from platium.scanners.deep.scanner import deep_search

class TestDeepScanner(unittest.TestCase):
    def test_email_detection(self):
        result = deep_search("test@example.com")
        self.assertEqual(result["detected_type"], "email")
        self.assertIn("results", result)

    def test_phone_detection(self):
        result = deep_search("+380991234567")
        self.assertEqual(result["detected_type"], "phone")

    def test_username_detection(self):
        result = deep_search("pnv21")
        self.assertEqual(result["detected_type"], "username")

if __name__ == "__main__":
    unittest.main()
