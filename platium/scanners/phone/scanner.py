import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from platium.core.config import load_config
from platium.core.errors import ScannerError

def search(phone, config=None, verbose=False):
    if config is None:
        config = load_config()
    
    results = {
        "target": phone,
        "scan_type": "phone",
        "sources": {}
    }
    
    try:
        number = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(number):
            results["status"] = "invalid"
            results["error"] = "Invalid phone number"
            return results
        
        results["sources"]["phonenumbers"] = {
            "status": "success",
            "country": geocoder.description_for_number(number, "en"),
            "operator": carrier.name_for_number(number, "en"),
            "timezone": timezone.time_zones_for_number(number)
        }
        results["status"] = "valid"
        
        # Додаткова перевірка через numverify (якщо є ключ)
        try:
            from platium.core.config import load_config
            config = load_config()
            if config.get("numverify_key"):
                import requests
                resp = requests.get(
                    f"http://apilayer.net/api/validate?access_key={config['numverify_key']}&number={phone}",
                    timeout=config.get("timeout", 10)
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results["sources"]["numverify"] = {
                        "status": "success",
                        "country": data.get('country_name', 'N/A'),
                        "location": data.get('location', 'N/A'),
                        "carrier": data.get('carrier', 'N/A'),
                        "line_type": data.get('line_type', 'N/A')
                    }
        except:
            pass
        
        # Заглушка для месенджерів
        results["sources"]["messengers"] = {
            "status": "info",
            "whatsapp": "Check manually",
            "telegram": "Check manually"
        }
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results
