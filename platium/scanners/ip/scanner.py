import requests
import socket
from platium.core.config import load_config
from platium.core.errors import ScannerError, NetworkError
from platium.utils.network import safe_request

def search(ip, config=None, verbose=False):
    if config is None:
        config = load_config()
    
    results = {
        "target": ip,
        "scan_type": "ip",
        "sources": {}
    }
    
    # 1. ip-api.com
    try:
        resp = safe_request(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as,proxy,hosting", timeout=config.get("timeout", 10))
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                results["sources"]["ip-api"] = {
                    "status": "success",
                    "country": data.get('country', 'N/A'),
                    "city": data.get('city', 'N/A'),
                    "isp": data.get('isp', 'N/A'),
                    "org": data.get('org', 'N/A'),
                    "as": data.get('as', 'N/A'),
                    "proxy": data.get('proxy', False),
                    "hosting": data.get('hosting', False)
                }
            else:
                results["sources"]["ip-api"] = {"status": "error", "error": data.get('message', 'Unknown error')}
        else:
            results["sources"]["ip-api"] = {"status": "error", "error": f"HTTP {resp.status_code if resp else 'unknown'}"}
    except Exception as e:
        results["sources"]["ip-api"] = {"status": "error", "error": str(e)}
    
    # 2. ipinfo.io (якщо є ключ)
    try:
        if config.get("ipinfo_key"):
            resp = safe_request(f"https://ipinfo.io/{ip}?token={config['ipinfo_key']}", timeout=config.get("timeout", 10))
            if resp and resp.status_code == 200:
                data = resp.json()
                results["sources"]["ipinfo"] = {
                    "status": "success",
                    "country": data.get('country', 'N/A'),
                    "region": data.get('region', 'N/A'),
                    "city": data.get('city', 'N/A'),
                    "loc": data.get('loc', 'N/A'),
                    "org": data.get('org', 'N/A'),
                    "timezone": data.get('timezone', 'N/A')
                }
            else:
                results["sources"]["ipinfo"] = {"status": "error", "error": f"HTTP {resp.status_code if resp else 'unknown'}"}
        else:
            results["sources"]["ipinfo"] = {"status": "skipped", "error": "API key missing"}
    except Exception as e:
        results["sources"]["ipinfo"] = {"status": "error", "error": str(e)}
    
    # 3. Whois
    try:
        import whois
        domain_info = whois.whois(ip)
        results["sources"]["whois"] = {
            "status": "success",
            "registrar": getattr(domain_info, 'registrar', 'N/A'),
            "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
            "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A'))
        }
    except Exception as e:
        results["sources"]["whois"] = {"status": "error", "error": str(e)}
    
    # Визначення проксі
    proxy_detected = False
    for source, data in results["sources"].items():
        if isinstance(data, dict) and data.get("proxy"):
            proxy_detected = True
            break
    
    results["proxy_detected"] = proxy_detected
    results["status"] = "success" if results["sources"] else "error"
    
    return results
