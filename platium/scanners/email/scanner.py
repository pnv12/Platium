import requests
from platium.core.config import load_config
from platium.core.errors import ScannerError, NetworkError, APILimitError
from platium.utils.network import safe_request

def search(email, config=None, verbose=False):
    if config is None:
        config = load_config()
    
    results = {
        "target": email,
        "scan_type": "email",
        "sources": {}
    }
    
    # 1. HIBP
    try:
        resp = safe_request(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=config.get("timeout", 10)
        )
        if resp and resp.status_code == 200:
            data = resp.json()
            results["sources"]["hibp"] = {
                "status": "found",
                "breaches": [b['Name'] for b in data],
                "count": len(data)
            }
        elif resp and resp.status_code == 404:
            results["sources"]["hibp"] = {"status": "clean", "breaches": [], "count": 0}
        else:
            results["sources"]["hibp"] = {"status": "error", "error": f"HTTP {resp.status_code if resp else 'unknown'}"}
    except Exception as e:
        results["sources"]["hibp"] = {"status": "error", "error": str(e)}
    
    # 2. LeakCheck
    try:
        resp = safe_request(f"https://leakcheck.net/api/v1/?check={email}", timeout=config.get("timeout", 10))
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get('found'):
                results["sources"]["leakcheck"] = {
                    "status": "found",
                    "sources": data.get('sources', []),
                    "count": len(data.get('sources', []))
                }
            else:
                results["sources"]["leakcheck"] = {"status": "clean"}
        else:
            results["sources"]["leakcheck"] = {"status": "error", "error": f"HTTP {resp.status_code if resp else 'unknown'}"}
    except Exception as e:
        results["sources"]["leakcheck"] = {"status": "error", "error": str(e)}
    
    found_sources = [k for k, v in results["sources"].items() if v.get("status") == "found"]
    if found_sources:
        results["status"] = "compromised"
        results["found_in"] = found_sources
    else:
        results["status"] = "clean"
    
    return results
