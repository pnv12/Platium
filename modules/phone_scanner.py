"""
Phone Scanner — аналіз номеру + месенджери
"""

import phonenumbers
from phonenumbers import carrier, geocoder, timezone

def search(phone):
    """Аналізує номер телефону"""
    results = {}
    
    try:
        number = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(number):
            results["error"] = "Невірний номер телефону"
            return results
        
        results["country"] = geocoder.description_for_number(number, "en")
        results["operator"] = carrier.name_for_number(number, "en")
        results["timezone"] = timezone.time_zones_for_number(number)
        
        # Додаткова перевірка через numverify (якщо є ключ)
        try:
            from config import NUMVERIFY_API_KEY
            url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone}&country_code=&format=1"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results["numverify"] = {
                    "country": data.get('country_name', 'N/A'),
                    "location": data.get('location', 'N/A'),
                    "carrier": data.get('carrier', 'N/A'),
                    "line_type": data.get('line_type', 'N/A')
                }
        except:
            pass
        
        # Месенджери (заглушка)
        results["messengers"] = {
            "whatsapp": "Перевірте вручну",
            "telegram": "Перевірте вручну"
        }
        
    except phonenumbers.NumberParseException as e:
        results["error"] = str(e)
    
    return results
