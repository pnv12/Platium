"""
Threat Intelligence — VirusTotal, Shodan
"""

import requests
import json

def check(query):
    """Перевіряє загрози через VirusTotal та Shodan"""
    results = {}
    
    # VirusTotal (без ключа — демо)
    try:
        response = requests.get(f"https://www.virustotal.com/api/v3/ip_addresses/{query}", timeout=5)
        if response.status_code == 200:
            results["virustotal"] = "IP знайдено"
        else:
            results["virustotal"] = "Не знайдено"
    except:
        results["virustotal"] = "Помилка підключення"
    
    # Shodan (демо)
    results["shodan"] = {
        "ports": [80, 443, 22],
        "country": "US",
        "isp": "Google LLC"
    }
    
    return results
