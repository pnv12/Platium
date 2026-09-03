import unittest
from platium.scanners.social.scanner import search

class TestSocialScanner(unittest.TestCase):
    def test_valid_username(self):
        result = search("pnv21")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "pnv21")
        self.assertIn("results", result)
        self.assertIsInstance(result["results"], dict)

    def test_empty_username(self):
        result = search("")
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
