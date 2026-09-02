"""
IP Scanner — геолокація, Shodan, whois
"""

import requests
import socket

def search(ip):
    """Аналізує IP-адресу"""
    results = {}
    
    # Геолокація через ip-api.com
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                results["country"] = data['country']
                results["city"] = data['city']
                results["isp"] = data['isp']
                results["org"] = data['org']
            else:
                results["geo_error"] = "Не вдалося визначити геолокацію"
    except Exception as e:
        results["geo_error"] = str(e)
    
    # Whois (базовий)
    try:
        import whois
        domain_info = whois.whois(ip)
        results["whois"] = {
            "registrar": domain_info.registrar,
            "creation_date": str(domain_info.creation_date),
            "expiration_date": str(domain_info.expiration_date),
        }
    except:
        pass
    
    return results
