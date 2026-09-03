import socket
import requests
from platium.core.config import load_config
from platium.core.errors import ScannerError, NetworkError
from platium.utils.network import safe_request

def search(ip, config=None, verbose=False):
    """
    Аналізує IP-адресу: геолокація, whois, проксі-детекція.
    """
    if config is None:
        config = load_config()
    
    results = {
        "target": ip,
        "scan_type": "ip",
        "status": "error",
        "data": {}
    }
    
    # 1. Геолокація через ip-api.com
    try:
        resp = safe_request(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as,proxy,hosting", timeout=config.get("timeout", 10))
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                results["data"]["location"] = {
                    "country": data.get('country', 'N/A'),
                    "city": data.get('city', 'N/A'),
                    "isp": data.get('isp', 'N/A'),
                    "org": data.get('org', 'N/A'),
                    "as": data.get('as', 'N/A'),
                    "proxy": data.get('proxy', False),
                    "hosting": data.get('hosting', False)
                }
                results["status"] = "success"
            else:
                results["status"] = "error"
                results["error"] = data.get('message', 'Unknown error')
        else:
            results["status"] = "error"
            results["error"] = f"HTTP {resp.status_code if resp else 'unknown'}"
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    # 2. WHOIS (опціонально)
    try:
        import whois
        domain_info = whois.whois(ip)
        results["data"]["whois"] = {
            "registrar": getattr(domain_info, 'registrar', 'N/A'),
            "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
            "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A')),
        }
    except:
        pass  # WHOIS не критичний
    
    return results
