"""
Threat Intelligence Scanner — VirusTotal, AbuseIPDB, Shodan
"""

import requests
from platium.core.config import load_config
from platium.utils.network import safe_request
from platium.core.errors import ScannerError

def search(target, config=None, verbose=False):
    """
    Перевірка IP/домену через VirusTotal, AbuseIPDB, Shodan.
    Повертає структурований результат з детальними статусами.
    """
    if config is None:
        config = load_config()

    result = {
        "target": target,
        "scan_type": "threat",
        "sources": {},
        "status": "empty"
    }

    timeout = config.get("timeout", 10)
    headers = {"User-Agent": "Mozilla/5.0"}

    # --- VirusTotal ---
    vt_key = config.get("virustotal_key")
    if not vt_key:
        result["sources"]["virustotal"] = {"status": "skipped", "message": "API key missing"}
    else:
        try:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{target}"
            headers = {"x-apikey": vt_key}
            resp = safe_request(url, headers=headers, timeout=timeout)
            if resp:
                if resp.status_code == 200:
                    data = resp.json()
                    result["sources"]["virustotal"] = {
                        "status": "success",
                        "data": {
                            "reputation": data.get("data", {}).get("attributes", {}).get("reputation"),
                            "country": data.get("data", {}).get("attributes", {}).get("country"),
                            "last_analysis_stats": data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                        }
                    }
                elif resp.status_code == 401:
                    result["sources"]["virustotal"] = {"status": "error", "message": "Invalid API key"}
                elif resp.status_code == 429:
                    result["sources"]["virustotal"] = {"status": "rate_limited", "message": "Rate limited"}
                else:
                    result["sources"]["virustotal"] = {"status": "error", "code": resp.status_code}
            else:
                result["sources"]["virustotal"] = {"status": "error", "message": "No response"}
        except Exception as e:
            result["sources"]["virustotal"] = {"status": "error", "message": str(e)}

    # --- AbuseIPDB ---
    abuse_key = config.get("abuseipdb_key")
    if not abuse_key:
        result["sources"]["abuseipdb"] = {"status": "skipped", "message": "API key missing"}
    else:
        try:
            url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={target}"
            headers = {"Key": abuse_key, "Accept": "application/json"}
            resp = safe_request(url, headers=headers, timeout=timeout)
            if resp:
                if resp.status_code == 200:
                    data = resp.json()
                    result["sources"]["abuseipdb"] = {
                        "status": "success",
                        "data": {
                            "abuse_score": data.get("data", {}).get("abuseConfidenceScore"),
                            "country": data.get("data", {}).get("countryCode"),
                            "total_reports": data.get("data", {}).get("totalReports")
                        }
                    }
                elif resp.status_code == 401:
                    result["sources"]["abuseipdb"] = {"status": "error", "message": "Invalid API key"}
                elif resp.status_code == 429:
                    result["sources"]["abuseipdb"] = {"status": "rate_limited", "message": "Rate limited"}
                else:
                    result["sources"]["abuseipdb"] = {"status": "error", "code": resp.status_code}
            else:
                result["sources"]["abuseipdb"] = {"status": "error", "message": "No response"}
        except Exception as e:
            result["sources"]["abuseipdb"] = {"status": "error", "message": str(e)}

    # --- Shodan ---
    shodan_key = config.get("shodan_key")
    if not shodan_key:
        result["sources"]["shodan"] = {"status": "skipped", "message": "API key missing"}
    else:
        try:
            url = f"https://api.shodan.io/shodan/host/{target}?key={shodan_key}"
            resp = safe_request(url, timeout=timeout)
            if resp:
                if resp.status_code == 200:
                    data = resp.json()
                    result["sources"]["shodan"] = {
                        "status": "success",
                        "data": {
                            "city": data.get("city"),
                            "country": data.get("country_name"),
                            "ports": data.get("ports", [])[:10],
                            "os": data.get("os"),
                            "isp": data.get("isp")
                        }
                    }
                elif resp.status_code == 401:
                    result["sources"]["shodan"] = {"status": "error", "message": "Invalid API key"}
                elif resp.status_code == 429:
                    result["sources"]["shodan"] = {"status": "rate_limited", "message": "Rate limited"}
                else:
                    result["sources"]["shodan"] = {"status": "error", "code": resp.status_code}
            else:
                result["sources"]["shodan"] = {"status": "error", "message": "No response"}
        except Exception as e:
            result["sources"]["shodan"] = {"status": "error", "message": str(e)}

    # Загальний статус
    success_count = sum(1 for s in result["sources"].values() if s.get("status") == "success")
    error_count = sum(1 for s in result["sources"].values() if s.get("status") in ("error", "rate_limited"))
    skipped_count = sum(1 for s in result["sources"].values() if s.get("status") == "skipped")

    if success_count > 0:
        result["status"] = "success"
    elif error_count > 0:
        result["status"] = "partial"
    elif skipped_count > 0:
        result["status"] = "skipped"
    else:
        result["status"] = "empty"

    return result
