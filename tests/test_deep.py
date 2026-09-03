import unittest
from platium.scanners.deep.scanner import deep_search, detect_type

class TestDeepScanner(unittest.TestCase):
    def test_detect_email(self):
        self.assertEqual(detect_type("test@example.com"), "email")

    def test_detect_phone(self):
        self.assertEqual(detect_type("+380991234567"), "phone")

    def test_detect_ip(self):
        self.assertEqual(detect_type("8.8.8.8"), "ip")

    def test_detect_username(self):
        self.assertEqual(detect_type("pnv21"), "username")

    def test_detect_unknown(self):
        self.assertEqual(detect_type(""), "unknown")
        self.assertEqual(detect_type("!@#$%"), "unknown")

    def test_deep_email(self):
        result = deep_search("test@example.com")
        self.assertEqual(result["detected_type"], "email")
        self.assertIn("results", result)

    def test_deep_phone(self):
        result = deep_search("+380991234567")
        self.assertEqual(result["detected_type"], "phone")
        self.assertIn("results", result)

    def test_deep_ip(self):
        result = deep_search("8.8.8.8")
        self.assertEqual(result["detected_type"], "ip")
        self.assertIn("results", result)

    def test_deep_username(self):
        result = deep_search("pnv21")
        self.assertEqual(result["detected_type"], "username")
        self.assertIn("results", result)

if __name__ == "__main__":
    unittest.main()
