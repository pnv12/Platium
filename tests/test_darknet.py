import unittest
from platium.scanners.darknet.scanner import search, check_tor

class TestDarknetScanner(unittest.TestCase):
    def test_search_without_tor(self):
        # Цей тест не перевіряє реальну роботу Tor, а тільки структуру
        result = search("bitcoin")
        self.assertIn("target", result)
        self.assertEqual(result["target"], "bitcoin")
        self.assertIn("sources", result)
        self.assertIn("status", result)

    def test_check_tor(self):
        # Просто перевіряємо, що функція не падає
        try:
            check_tor()
            self.assertTrue(True)
        except:
            self.fail("check_tor() raised exception")

if __name__ == "__main__":
    unittest.main()
