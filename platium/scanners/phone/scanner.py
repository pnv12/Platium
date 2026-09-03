import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from platium.core.errors import ScannerError, ValidationError
from platium.core.config import load_config

def search(phone, config=None, verbose=False):
    """
    Аналізує номер телефону: країна, оператор, часовий пояс.
    """
    if config is None:
        config = load_config()
    
    results = {
        "target": phone,
        "scan_type": "phone",
        "status": "error",
        "data": {}
    }
    
    try:
        number = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(number):
            results["status"] = "invalid"
            results["error"] = "Invalid phone number"
            return results
        
        results["data"] = {
            "country": geocoder.description_for_number(number, "en"),
            "operator": carrier.name_for_number(number, "en"),
            "timezone": str(timezone.time_zones_for_number(number)),
            "is_valid": True
        }
        results["status"] = "success"
        
    except phonenumbers.NumberParseException as e:
        results["status"] = "error"
        results["error"] = str(e)
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results
