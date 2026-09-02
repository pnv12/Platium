"""
Graph Builder — побудова графу зв'язків
"""

import requests

def build(email):
    """Будує граф зв'язків на основі email"""
    results = {}
    
    # 1. SecurityTrails (якщо є ключ)
    try:
        from config import SECURITYTRAILS_API_KEY
        url = f"https://api.securitytrails.com/v1/email/{email}"
        headers = {"APIKEY": SECURITYTRAILS_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results["securitytrails"] = data
        else:
            results["securitytrails"] = {"error": f"HTTP {response.status_code}"}
    except:
        results["securitytrails"] = {"error": "Ключ не знайдено"}
    
    # 2. Spyse (демо)
    results["spyse"] = {"note": "Перевірте вручну через Spyse"}
    
    # 3. Локальна заглушка
    results["connections"] = ["pnv21", "neo", "saturn"]
    results["links"] = 3
    
    return results
