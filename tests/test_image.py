import os
import tempfile
import unittest

from PIL import Image

from platium.scanners.image.scanner import search


class TestImageScanner(unittest.TestCase):
    def test_missing_file(self):
        result = search("nonexistent-image.jpg")

        self.assertEqual(result.status.value, "error")
        self.assertIn("File not found", result.error)

    def test_empty_path(self):
        result = search("")

        self.assertEqual(result.status.value, "error")
        self.assertEqual(result.error, "Image path is required")

    def test_image_analysis(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "test-image.png")

            image = Image.new("RGB", (32, 16), "white")
            image.save(image_path, format="PNG")

            result = search(image_path)

            self.assertEqual(result.status.value, "success")
            self.assertEqual(result.target, image_path)
            self.assertEqual(result.scanner, "image")

            self.assertIn("file", result.data)
            self.assertIn("image", result.data)
            self.assertIn("fingerprint", result.data)

            self.assertEqual(result.data["image"]["format"], "PNG")
            self.assertEqual(result.data["image"]["width"], 32)
            self.assertEqual(result.data["image"]["height"], 16)
            self.assertEqual(result.data["image"]["mode"], "RGB")

            fingerprint = result.data["fingerprint"]
            self.assertEqual(len(fingerprint["sha256"]), 64)
            self.assertEqual(len(fingerprint["average_hash"]), 64)
            self.assertTrue(all(
                bit in "01"
                for bit in fingerprint["average_hash"]
            ))

            self.assertIn("image", result.sources)
            self.assertIn("hash", result.sources)
            self.assertIn("Image file validated", result.evidence)


if __name__ == "__main__":
    unittest.main()
