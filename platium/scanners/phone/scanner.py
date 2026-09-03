import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from platium.core.config import load_config
from platium.core.errors import ValidationError, ScannerError

def search(phone, config=None, verbose=False):
    """
    Аналізує номер телефону: країна, оператор, часовий пояс.
    Повертає структурований результат.
    """
    if config is None:
        config = load_config()
    
    result = {
        "target": phone,
        "scan_type": "phone",
        "status": "unknown",
        "data": {}
    }
    
    try:
        number = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(number):
            result["status"] = "invalid"
            result["error"] = "Invalid phone number"
            return result
        
        result["data"]["country"] = geocoder.description_for_number(number, "en")
        result["data"]["operator"] = carrier.name_for_number(number, "en")
        result["data"]["timezone"] = timezone.time_zones_for_number(number)
        result["status"] = "valid"
        
    except phonenumbers.NumberParseException as e:
        result["status"] = "error"
        result["error"] = str(e)
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result
