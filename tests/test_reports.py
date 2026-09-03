import unittest
import os
import json
from platium.reports.generator import generate, REPORTS_DIR

class TestReportGenerator(unittest.TestCase):
    def test_generate_reports(self):
        data = {"test": "data", "target": "example", "status": "success"}
        result = generate(data, "test_report")
        self.assertIn("txt", result)
        self.assertIn("json", result)
        self.assertIn("html", result)

        # Перевіряємо, що файли створилися
        self.assertTrue(os.path.exists(result["txt"]))
        self.assertTrue(os.path.exists(result["json"]))
        self.assertTrue(os.path.exists(result["html"]))

    def test_generate_empty_data(self):
        with self.assertRaises(Exception):
            generate({})

    def test_generate_without_path(self):
        data = {"test": "data"}
        result = generate(data)
        self.assertIn("txt", result)
        self.assertIn("json", result)
        self.assertIn("html", result)

if __name__ == "__main__":
    unittest.main()
