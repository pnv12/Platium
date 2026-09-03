import requests
from platium.core.config import load_config
from platium.core.errors import ScannerError
from platium.utils.network import safe_request

def search(ip_or_domain, config=None, verbose=False):
    """
    Перевіряє IP або домен через VirusTotal, AbuseIPDB (якщо є ключі).
    """
    if config is None:
        config = load_config()
    
    results = {
        "target": ip_or_domain,
        "scan_type": "threat",
        "status": "error",
        "data": {}
    }
    
    # VirusTotal (якщо є ключ)
    vt_key = config.get("virustotal_key")
    if vt_key:
        try:
            resp = safe_request(
                f"https://www.virustotal.com/api/v3/ip_addresses/{ip_or_domain}",
                headers={"x-apikey": vt_key},
                timeout=config.get("timeout", 10)
            )
            if resp and resp.status_code == 200:
                data = resp.json()
                results["data"]["virustotal"] = {
                    "status": "found",
                    "data": data
                }
            else:
                results["data"]["virustotal"] = {
                    "status": "error",
                    "error": f"HTTP {resp.status_code if resp else 'unknown'}"
                }
        except Exception as e:
            results["data"]["virustotal"] = {"status": "error", "error": str(e)}
    else:
        results["data"]["virustotal"] = {"status": "skipped", "reason": "API key missing"}
    
    # AbuseIPDB (якщо є ключ)
    abuse_key = config.get("abuseipdb_key")
    if abuse_key:
        try:
            resp = safe_request(
                f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip_or_domain}",
                headers={"Key": abuse_key, "Accept": "application/json"},
                timeout=config.get("timeout", 10)
            )
            if resp and resp.status_code == 200:
                data = resp.json()
                results["data"]["abuseipdb"] = {
                    "status": "found",
                    "data": data
                }
            else:
                results["data"]["abuseipdb"] = {
                    "status": "error",
                    "error": f"HTTP {resp.status_code if resp else 'unknown'}"
                }
        except Exception as e:
            results["data"]["abuseipdb"] = {"status": "error", "error": str(e)}
    else:
        results["data"]["abuseipdb"] = {"status": "skipped", "reason": "API key missing"}
    
    results["status"] = "success"
    return results
