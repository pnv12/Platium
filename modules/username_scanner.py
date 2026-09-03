import concurrent.futures
from platium.core.config import get_user_agent
from platium.utils.network import safe_request

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    # ... інші
}

def search(username, config, verbose=False):
    results = {}
    headers = {"User-Agent": get_user_agent()}
    
    def check_platform(name, url):
        try:
            resp = safe_request(url.format(username), headers=headers, timeout=config.get("timeout", 10))
            if resp and resp.status_code == 200:
                return name, {"found": True, "url": url.format(username)}
            else:
                return name, {"found": False, "url": url.format(username)}
        except Exception as e:
            return name, {"found": "error", "error": str(e)}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_platform, name, url): name for name, url in PLATFORMS.items()}
        for future in concurrent.futures.as_completed(futures):
            name, result = future.result()
            results[name] = result
    
    return results
