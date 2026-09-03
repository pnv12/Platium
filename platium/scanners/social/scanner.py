import requests
from platium.core.config import load_config
from platium.utils.network import safe_request

def search(username, config=None, verbose=False):
    """
    Аналізує профіль у соцмережах.
    """
    if config is None:
        config = load_config()
    
    results = {
        "target": username,
        "scan_type": "social",
        "status": "error",
        "data": {}
    }
    
    platforms = {
        "Twitter": f"https://nitter.net/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
    }
    
    for name, url in platforms.items():
        try:
            resp = safe_request(url, timeout=config.get("timeout", 10))
            if resp and resp.status_code == 200:
                results["data"][name] = {"found": True, "url": url}
            else:
                results["data"][name] = {"found": False}
        except Exception as e:
            results["data"][name] = {"found": "Error", "error": str(e)}
    
    results["status"] = "success"
    return results
