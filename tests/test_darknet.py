import unittest
from platium.scanners.darknet.scanner import search

class TestDarknetScanner(unittest.TestCase):
    def test_valid_query(self):
        result = search("bitcoin")
        self.assertIn("query", result)
        self.assertEqual(result["query"], "bitcoin")
        self.assertIn("results", result)

    def test_empty_query(self):
        result = search("")
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
