"""
Email Scanner — перевірка на витік даних
"""

import requests

def search(email):
    """Перевіряє email через Have I Been Pwned"""
    results = {}
    
    # HIBP API
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            breaches = response.json()
            results["breaches"] = [b['Name'] for b in breaches]
        elif response.status_code == 404:
            results["breaches"] = []
        else:
            results["error"] = f"HTTP {response.status_code}"
    except Exception as e:
        results["error"] = str(e)
    
    # Пошук в публічних базах (заглушка)
    results["public_databases"] = "Перевірка вручну або через додаткові API"
    
    return results
