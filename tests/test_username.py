import unittest
from platium.scanners.username.scanner import search
from platium.core.validators import validate_username

class TestUsernameScanner(unittest.TestCase):
    def test_valid_username(self):
        result = search("testuser")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "testuser")
        self.assertIn("sources", result)
        self.assertIn("status", result)

    def test_invalid_username_validation(self):
        with self.assertRaises(ValidationError):
            validate_username("a")

    def test_search_empty(self):
        result = search("")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "empty")

if __name__ == "__main__":
    unittest.main()
