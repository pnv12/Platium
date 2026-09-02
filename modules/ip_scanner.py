"""
IP Scanner — геолокація, Shodan, whois, проксі-детекція
"""

import requests
import socket
import concurrent.futures
from config import SHODAN_API_KEY

def search(ip):
    """Аналізує IP-адресу з використанням кількох джерел"""
    results = {}
    
    # 1. Геолокація через ip-api.com (швидко)
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as,proxy,hosting", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                results["location"] = {
                    "country": data.get('country', 'N/A'),
                    "city": data.get('city', 'N/A'),
                    "isp": data.get('isp', 'N/A'),
                    "org": data.get('org', 'N/A'),
                    "as": data.get('as', 'N/A'),
                    "proxy": data.get('proxy', False),
                    "hosting": data.get('hosting', False)
                }
    except Exception as e:
        results["geo_error"] = str(e)
    
    # 2. Додаткова геолокація через ipinfo.io (якщо є ключ)
    try:
        from config import IPINFO_API_KEY
        response = requests.get(f"https://ipinfo.io/{ip}?token={IPINFO_API_KEY}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results["location_detail"] = {
                "country": data.get('country', 'N/A'),
                "region": data.get('region', 'N/A'),
                "city": data.get('city', 'N/A'),
                "loc": data.get('loc', 'N/A'),
                "org": data.get('org', 'N/A'),
                "timezone": data.get('timezone', 'N/A')
            }
    except:
        pass
    
    # 3. Whois
    try:
        import whois
        domain_info = whois.whois(ip)
        results["whois"] = {
            "registrar": getattr(domain_info, 'registrar', 'N/A'),
            "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
            "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A')),
        }
    except:
        pass
    
    # 4. Shodan (якщо є ключ)
    if SHODAN_API_KEY:
        try:
            import shodan
            api = shodan.Shodan(SHODAN_API_KEY)
            host = api.host(ip)
            results["shodan"] = {
                "ports": host.get('ports', []),
                "vulns": host.get('vulns', []),
                "isp": host.get('isp', 'N/A'),
                "org": host.get('org', 'N/A')
            }
        except:
            pass
    
    # 5. Визначення проксі/VPN
    if results.get("location", {}).get("proxy"):
        results["proxy_detected"] = True
    else:
        results["proxy_detected"] = False
    
    return results
