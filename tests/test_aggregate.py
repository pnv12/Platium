import unittest
import os
import json
from platium.intelligence.aggregator import init_db, save_search, find_connections, generate_analysis_report, DB_PATH

class TestAggregator(unittest.TestCase):
    def setUp(self):
        # Переконаємося, що база ініціалізована
        init_db()

    def test_init_db(self):
        self.assertTrue(os.path.exists(DB_PATH))

    def test_save_and_find(self):
        save_search("testuser", "username", {"status": "ok"})
        conns = find_connections("testuser")
        self.assertIsInstance(conns, list)

    def test_analyze_report(self):
        report = generate_analysis_report()
        self.assertIn("total_queries", report)
        self.assertIn("connections", report)
        self.assertIn("type_distribution", report)

if __name__ == "__main__":
    unittest.main()
