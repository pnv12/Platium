"""
Threat Scanner — перевірка IP/доменів на загрози (оновлена версія)
"""

import requests
from platium.core.result import ScanResult, ScanStatus
from platium.core.config import load_config
from platium.utils.network import safe_request
from platium.core.errors import APILimitError, NetworkError

def search(query, config=None, verbose=False) -> ScanResult:
    """
    Перевіряє IP/домен на загрози через VirusTotal та AbuseIPDB.
    Повертає ScanResult з єдиним контрактом.
    """
    if config is None:
        config = load_config()

    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND
    errors = []

    # 1. VirusTotal
    vt_key = config.get("virustotal_key")
    if vt_key:
        try:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{query}"
            headers = {"x-apikey": vt_key}
            resp = safe_request(url, headers=headers, timeout=config.get("timeout", 10))
            if resp is None:
                sources["virustotal"] = {"status": "error", "message": "No response"}
                errors.append("VirusTotal: no response")
            elif resp.status_code == 200:
                vt_data = resp.json()
                sources["virustotal"] = {"status": "success", "data": vt_data}
                data["virustotal"] = vt_data
                status = ScanStatus.SUCCESS
            elif resp.status_code == 401:
                sources["virustotal"] = {"status": "error", "code": 401, "message": "Invalid API key"}
                errors.append("VirusTotal: invalid API key")
            elif resp.status_code == 429:
                sources["virustotal"] = {"status": "rate_limited", "code": 429, "message": "Rate limit exceeded"}
                errors.append("VirusTotal: rate limited")
            else:
                sources["virustotal"] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
                errors.append(f"VirusTotal: HTTP {resp.status_code}")
        except Exception as e:
            sources["virustotal"] = {"status": "error", "message": str(e)}
            errors.append(f"VirusTotal: {str(e)}")
    else:
        sources["virustotal"] = {"status": "skipped", "message": "No API key"}
        errors.append("VirusTotal: skipped (no key)")

    # 2. AbuseIPDB
    abuse_key = config.get("abuseipdb_key")
    if abuse_key:
        try:
            url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={query}"
            headers = {"Key": abuse_key, "Accept": "application/json"}
            resp = safe_request(url, headers=headers, timeout=config.get("timeout", 10))
            if resp is None:
                sources["abuseipdb"] = {"status": "error", "message": "No response"}
                errors.append("AbuseIPDB: no response")
            elif resp.status_code == 200:
                abuse_data = resp.json()
                sources["abuseipdb"] = {"status": "success", "data": abuse_data}
                data["abuseipdb"] = abuse_data
                if status != ScanStatus.SUCCESS:
                    status = ScanStatus.PARTIAL
            elif resp.status_code == 401:
                sources["abuseipdb"] = {"status": "error", "code": 401, "message": "Invalid API key"}
                errors.append("AbuseIPDB: invalid API key")
            elif resp.status_code == 429:
                sources["abuseipdb"] = {"status": "rate_limited", "code": 429, "message": "Rate limit exceeded"}
                errors.append("AbuseIPDB: rate limited")
            else:
                sources["abuseipdb"] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
                errors.append(f"AbuseIPDB: HTTP {resp.status_code}")
        except Exception as e:
            sources["abuseipdb"] = {"status": "error", "message": str(e)}
            errors.append(f"AbuseIPDB: {str(e)}")
    else:
        sources["abuseipdb"] = {"status": "skipped", "message": "No API key"}
        errors.append("AbuseIPDB: skipped (no key)")

    # Визначаємо загальний статус
    if status == ScanStatus.NOT_FOUND and errors:
        # Якщо всі джерела пропущені або помилкові
        if all(s.get("status") in ("skipped", "error", "rate_limited") for s in sources.values()):
            status = ScanStatus.ERROR
        else:
            status = ScanStatus.PARTIAL

    if status == ScanStatus.SUCCESS and errors:
        status = ScanStatus.PARTIAL

    # Якщо всі джерела пропущені — не вважаємо це success
    if all(s.get("status") == "skipped" for s in sources.values()):
        status = ScanStatus.SKIPPED
        errors = ["All sources skipped (no API keys)"]

    # Створюємо результат
    result = ScanResult(
        target=query,
        scanner="threat",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.9 if status == ScanStatus.SUCCESS else 0.1,
        evidence=[f"Checked {len(sources)} sources"]
    )

    return result
