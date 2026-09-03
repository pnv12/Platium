"""
Threat Intelligence Scanner — VirusTotal, AbuseIPDB, Shodan
"""

import requests
from platium.core.config import load_config
from platium.core.errors import ScannerError

def search(query, config=None, verbose=False):
    """
    Перевіряє IP/домен через VirusTotal, AbuseIPDB, Shodan.
    Повертає структурований результат з детальними статусами.
    """
    if config is None:
        config = load_config()

    result = {
        "target": query,
        "scan_type": "threat",
        "sources": {},
        "status": "skipped"
    }

    timeout = config.get("timeout", 10)

    # 1. VirusTotal
    vt_key = config.get("virustotal_key")
    if not vt_key:
        result["sources"]["virustotal"] = {"status": "skipped", "message": "API key missing"}
    else:
        try:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{query}"
            headers = {"x-apikey": vt_key}
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                result["sources"]["virustotal"] = {
                    "status": "success",
                    "data": data.get("data", {}),
                    "code": 200
                }
            elif resp.status_code == 401:
                result["sources"]["virustotal"] = {"status": "error", "message": "Invalid API key", "code": 401}
            elif resp.status_code == 429:
                result["sources"]["virustotal"] = {"status": "rate_limited", "message": "Too many requests", "code": 429}
            else:
                result["sources"]["virustotal"] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
        except Exception as e:
            result["sources"]["virustotal"] = {"status": "error", "message": str(e)}

    # 2. AbuseIPDB
    abuse_key = config.get("abuseipdb_key")
    if not abuse_key:
        result["sources"]["abuseipdb"] = {"status": "skipped", "message": "API key missing"}
    else:
        try:
            url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={query}"
            headers = {"Key": abuse_key, "Accept": "application/json"}
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                result["sources"]["abuseipdb"] = {
                    "status": "success",
                    "data": data.get("data", {}),
                    "code": 200
                }
            elif resp.status_code == 401:
                result["sources"]["abuseipdb"] = {"status": "error", "message": "Invalid API key", "code": 401}
            elif resp.status_code == 429:
                result["sources"]["abuseipdb"] = {"status": "rate_limited", "message": "Too many requests", "code": 429}
            else:
                result["sources"]["abuseipdb"] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
        except Exception as e:
            result["sources"]["abuseipdb"] = {"status": "error", "message": str(e)}

    # 3. Shodan
    shodan_key = config.get("shodan_key")
    if not shodan_key:
        result["sources"]["shodan"] = {"status": "skipped", "message": "API key missing"}
    else:
        try:
            import shodan
            api = shodan.Shodan(shodan_key)
            host = api.host(query)
            result["sources"]["shodan"] = {
                "status": "success",
                "data": {
                    "ports": host.get("ports", []),
                    "isp": host.get("isp", "N/A"),
                    "org": host.get("org", "N/A"),
                    "vulns": host.get("vulns", [])
                },
                "code": 200
            }
        except shodan.APIError as e:
            if "API key" in str(e):
                result["sources"]["shodan"] = {"status": "error", "message": "Invalid API key"}
            else:
                result["sources"]["shodan"] = {"status": "error", "message": str(e)}
        except Exception as e:
            result["sources"]["shodan"] = {"status": "error", "message": str(e)}

    # Загальний статус
    success_count = sum(1 for s in result["sources"].values() if s.get("status") == "success")
    error_count = sum(1 for s in result["sources"].values() if s.get("status") == "error")
    skipped_count = sum(1 for s in result["sources"].values() if s.get("status") == "skipped")

    if success_count > 0:
        result["status"] = "success"
    elif error_count > 0 and success_count == 0:
        result["status"] = "partial"
    elif skipped_count == len(result["sources"]):
        result["status"] = "skipped"
    else:
        result["status"] = "empty"

    return result
