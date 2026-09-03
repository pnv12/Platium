import unittest
from platium.intelligence.aggregator import init_db, save_search, find_connections

class TestAggregator(unittest.TestCase):
    def test_init_db(self):
        try:
            init_db()
            self.assertTrue(True)
        except Exception:
            self.fail("init_db() raised exception")

    def test_save_search(self):
        try:
            save_search("test", "username", {"status": "ok"})
            self.assertTrue(True)
        except Exception:
            self.fail("save_search() raised exception")

if __name__ == "__main__":
    unittest.main()
