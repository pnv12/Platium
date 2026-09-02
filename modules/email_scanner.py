"""
Email Scanner — перевірка на витік даних + соцмережі
"""

import requests

def search(email):
    """Перевіряє email на витік, соцмережі, спам-лісти"""
    results = {}
    
    # 1. HIBP
    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            breaches = response.json()
            results["hibp"] = {"breaches": [b['Name'] for b in breaches]}
        elif response.status_code == 404:
            results["hibp"] = {"breaches": []}
        else:
            results["hibp"] = {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        results["hibp"] = {"error": str(e)}
    
    # 2. LeakCheck (без ключа — демо)
    try:
        url = f"https://leakcheck.net/api/v1/?check={email}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('found'):
                results["leakcheck"] = {"found": True, "sources": data.get('sources', [])}
            else:
                results["leakcheck"] = {"found": False}
        else:
            results["leakcheck"] = {"error": f"HTTP {response.status_code}"}
    except:
        results["leakcheck"] = {"error": "Помилка з'єднання"}
    
    # 3. Пошук у соцмережах (заглушка)
    results["social"] = {"note": "Перевірте вручну Instagram, Twitter, Facebook"}
    
    # 4. Спам-лісти (заглушка)
    results["spam_lists"] = {"note": "Перевірте через публічні списки"}
    
    return results
