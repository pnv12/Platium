import unittest
from platium.scanners.social.scanner import search

class TestSocialScanner(unittest.TestCase):
    def test_valid_username(self):
        result = search("pnv21")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "pnv21")
        self.assertIn("sources", result)
        self.assertIn("status", result)

    def test_invalid_username(self):
        result = search("invalid_user_xyz_123")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "invalid_user_xyz_123")
        self.assertIn("sources", result)
        self.assertIn("status", result)

    def test_empty_username(self):
        result = search("")
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

if __name__ == "__main__":
    unittest.main()
