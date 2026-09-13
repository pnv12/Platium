import os
import tempfile
import unittest

from PIL import Image

from platium.core.normalizer import normalize_result
from platium.scanners.image.metadata import _convert_gps_coordinate
from platium.scanners.image.scanner import search
from platium.storage import database


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
            image_path = os.path.join(
                temp_dir,
                "test-image.png"
            )

            image = Image.new(
                "RGB",
                (32, 16),
                "white"
            )
            image.save(
                image_path,
                format="PNG"
            )

            result = search(image_path)

            self.assertEqual(
                result.status.value,
                "success"
            )
            self.assertEqual(
                result.target,
                image_path
            )
            self.assertEqual(
                result.scanner,
                "image"
            )

            self.assertIn(
                "file",
                result.data
            )
            self.assertIn(
                "image",
                result.data
            )
            self.assertIn(
                "metadata",
                result.data
            )
            self.assertIn(
                "fingerprint",
                result.data
            )

            self.assertEqual(
                result.data["image"]["format"],
                "PNG"
            )
            self.assertEqual(
                result.data["image"]["width"],
                32
            )
            self.assertEqual(
                result.data["image"]["height"],
                16
            )
            self.assertEqual(
                result.data["image"]["mode"],
                "RGB"
            )

            exif = result.data["metadata"]["exif"]

            self.assertIn(
                "available",
                exif
            )
            self.assertIn(
                "fields",
                exif
            )
            self.assertIn(
                "gps_present",
                exif
            )
            self.assertIn(
                "gps",
                exif
            )

            self.assertFalse(
                exif["available"]
            )
            self.assertEqual(
                exif["fields"],
                {}
            )
            self.assertFalse(
                exif["gps_present"]
            )

            gps = exif["gps"]

            self.assertFalse(
                gps["present"]
            )
            self.assertIsNone(
                gps["latitude"]
            )
            self.assertIsNone(
                gps["longitude"]
            )

            fingerprint = result.data["fingerprint"]

            self.assertEqual(
                len(fingerprint["sha256"]),
                64
            )
            self.assertEqual(
                len(fingerprint["average_hash"]),
                64
            )
            self.assertTrue(
                all(
                    bit in "01"
                    for bit in fingerprint["average_hash"]
                )
            )

            self.assertIn(
                "image",
                result.sources
            )
            self.assertIn(
                "metadata",
                result.sources
            )
            self.assertIn(
                "hash",
                result.sources
            )

            self.assertIn(
                "Image file validated",
                result.evidence
            )
            self.assertIn(
                "EXIF metadata analyzed",
                result.evidence
            )

    def test_gps_coordinate_conversion(self):
        coordinate = _convert_gps_coordinate(
            (50, 30, 0)
        )

        self.assertAlmostEqual(
            coordinate,
            50.5
        )

    def test_gps_coordinate_invalid(self):
        self.assertIsNone(
            _convert_gps_coordinate(
                (50, 30)
            )
        )

        self.assertIsNone(
            _convert_gps_coordinate(
                None
            )
        )

    def test_image_normalization_and_storage(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(
                temp_dir,
                "integration-image.png"
            )
            database_path = os.path.join(
                temp_dir,
                "test-platium.db"
            )

            image = Image.new(
                "RGB",
                (32, 16),
                "white"
            )
            image.save(
                image_path,
                format="PNG"
            )

            original_db_path = database.DB_PATH
            database.DB_PATH = database_path

            try:
                result = search(image_path)

                self.assertEqual(
                    result.status.value,
                    "success"
                )

                normalized = normalize_result(result)

                self.assertIn(
                    "entity_id",
                    normalized
                )
                self.assertIn(
                    "observations",
                    normalized
                )

                entity_id = normalized["entity_id"]

                entity = database.get_entity_by_id(
                    entity_id
                )

                self.assertIsNotNone(entity)
                self.assertEqual(
                    entity["entity_type"],
                    "image"
                )
                self.assertEqual(
                    entity["value"],
                    image_path
                )

                observations = database.get_observations(
                    entity_id
                )

                self.assertEqual(
                    len(observations),
                    3
                )

                metadata_observation = next(
                    observation
                    for observation in observations
                    if observation["source"] == "metadata"
                )

                self.assertEqual(
                    metadata_observation["scanner"],
                    "image"
                )
                self.assertEqual(
                    metadata_observation["status"],
                    "success"
                )
                self.assertIsInstance(
                    metadata_observation["data"],
                    dict
                )
                self.assertIn(
                    "available",
                    metadata_observation["data"]
                )
                self.assertIn(
                    "fields",
                    metadata_observation["data"]
                )
                self.assertIn(
                    "gps_present",
                    metadata_observation["data"]
                )
                self.assertIn(
                    "gps",
                    metadata_observation["data"]
                )

                relationships = database.get_relationships(
                    entity_id,
                    direction="outgoing"
                )

                relation_types = {
                    relationship["relation_type"]
                    for relationship in relationships
                }

                self.assertIn(
                    "has_sha256",
                    relation_types
                )
                self.assertIn(
                    "has_perceptual_hash",
                    relation_types
                )

                self.assertEqual(
                    len(relationships),
                    2
                )

            finally:
                database.DB_PATH = original_db_path


if __name__ == "__main__":
    unittest.main()
