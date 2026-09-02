"""
Darknet Scanner — пошук у даркнеті
"""

import requests

def search(query):
    """Пошук .onion сайтів через Ahmia"""
    results = {}
    try:
        response = requests.get(f"https://ahmia.fi/search/?q={query}", timeout=10)
        if response.status_code == 200:
            results["url"] = "https://ahmia.fi/search/?q=" + query
            results["note"] = "Скопіюйте посилання та відкрийте в Tor Browser"
        else:
            results["error"] = "Помилка підключення до Ahmia"
    except Exception as e:
        results["error"] = str(e)
    
    return results
