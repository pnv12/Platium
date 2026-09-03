import unittest
from platium.core.validators import validate_username
from platium.core.errors import ValidationError

class TestUsername(unittest.TestCase):
    def test_valid_username(self):
        self.assertIsNone(validate_username("testuser"))
    
    def test_invalid_username_short(self):
        with self.assertRaises(ValidationError):
            validate_username("a")
    
    def test_invalid_username_chars(self):
        with self.assertRaises(ValidationError):
            validate_username("test user!")

if __name__ == "__main__":
    unittest.main()
