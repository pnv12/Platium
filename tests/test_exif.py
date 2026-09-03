import unittest
from platium.scanners.exif.scanner import search

class TestEXIFScanner(unittest.TestCase):
    def test_missing_file(self):
        result = search("nonexistent.jpg")
        self.assertIn("error", result)

    def test_empty_path(self):
        result = search("")
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
