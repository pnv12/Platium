"""
Phone Scanner — аналіз номеру телефону
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
        
    except phonenumbers.NumberParseException as e:
        results["error"] = str(e)
    
    return results
