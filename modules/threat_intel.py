"""
Threat Intelligence — VirusTotal, AbuseIPDB, Shodan
"""

import requests

def check(query):
    """Перевіряє загрози через VirusTotal, AbuseIPDB, Shodan"""
    results = {}
    
    # 1. VirusTotal (якщо є ключ)
    try:
        from config import VIRUSTOTAL_API_KEY
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{query}"
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results["virustotal"] = data
        else:
            results["virustotal"] = {"error": f"HTTP {response.status_code}"}
    except:
        results["virustotal"] = {"error": "Ключ не знайдено"}
    
    # 2. AbuseIPDB
    try:
        from config import ABUSEIPDB_API_KEY
        url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={query}"
        headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results["abuseipdb"] = data
        else:
            results["abuseipdb"] = {"error": f"HTTP {response.status_code}"}
    except:
        results["abuseipdb"] = {"error": "Ключ не знайдено"}
    
    # 3. Відкриті порти (Shodan, якщо є ключ)
    try:
        from config import SHODAN_API_KEY
        import shodan
        api = shodan.Shodan(SHODAN_API_KEY)
        host = api.host(query)
        results["shodan"] = {"ports": host.get('ports', [])}
    except:
        results["shodan"] = {"error": "Shodan недоступний"}
    
    return results
