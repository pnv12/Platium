import requests
from platium.core.config import config
from platium.core.result import ScanResult, ScanStatus
from platium.utils.network import safe_request

def search(email, verbose=False):
    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND
    errors = []
    timeout = config.timeout

    hibp_key = config.get_api_key("hibp_key")
    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = safe_request(url, headers=headers, timeout=timeout)

        if resp is None:
            sources["hibp"] = {"status": "error", "message": "No response"}
            errors.append("HIBP: no response")
        elif resp.status_code == 200:
            breaches = resp.json()
            sources["hibp"] = {"status": "success", "count": len(breaches), "breaches": [b['Name'] for b in breaches]}
            data["hibp"] = breaches
            status = ScanStatus.SUCCESS
        elif resp.status_code == 404:
            sources["hibp"] = {"status": "not_found", "message": "Email not found in breaches"}
        elif resp.status_code == 429:
            sources["hibp"] = {"status": "rate_limited", "message": "Rate limit exceeded"}
            errors.append("HIBP: rate limited")
        else:
            sources["hibp"] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
            errors.append(f"HIBP: HTTP {resp.status_code}")
    except Exception as e:
        sources["hibp"] = {"status": "error", "message": str(e)}
        errors.append(f"HIBP: {str(e)}")

    try:
        url = f"https://leakcheck.net/api/v1/?check={email}"
        resp = safe_request(url, timeout=timeout)
        if resp is None:
            sources["leakcheck"] = {"status": "error", "message": "No response"}
            errors.append("LeakCheck: no response")
        elif resp.status_code == 200:
            leak_data = resp.json()
            if leak_data.get('found'):
                sources["leakcheck"] = {"status": "success", "sources": leak_data.get('sources', [])}
                data["leakcheck"] = leak_data
                if status != ScanStatus.SUCCESS:
                    status = ScanStatus.PARTIAL
            else:
                sources["leakcheck"] = {"status": "not_found", "message": "Not found in leakcheck"}
        elif resp.status_code == 429:
            sources["leakcheck"] = {"status": "rate_limited", "message": "Rate limit exceeded"}
            errors.append("LeakCheck: rate limited")
        else:
            sources["leakcheck"] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
            errors.append(f"LeakCheck: HTTP {resp.status_code}")
    except Exception as e:
        sources["leakcheck"] = {"status": "error", "message": str(e)}
        errors.append(f"LeakCheck: {str(e)}")

    if status == ScanStatus.NOT_FOUND and errors:
        status = ScanStatus.PARTIAL if len(errors) < len(sources) else ScanStatus.ERROR

    if status == ScanStatus.SUCCESS and errors:
        status = ScanStatus.PARTIAL

    if status == ScanStatus.SUCCESS and not data:
        status = ScanStatus.NOT_FOUND

    result = ScanResult(
        target=email,
        scanner="email",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.8 if status == ScanStatus.SUCCESS else 0.2,
        evidence=[f"Checked {len(sources)} sources"]
    )
    return result
