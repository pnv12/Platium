import requests
from bs4 import BeautifulSoup
from platium.core.config import load_config
from platium.core.errors import ScannerError
from platium.utils.network import safe_request

def search(query, config=None, verbose=False):
    """
    Пошук у даркнеті через Ahmia (з підтримкою Tor, якщо він запущений).
    Повертає структурований результат.
    """
    if config is None:
        config = load_config()

    result = {
        "target": query,
        "scan_type": "darknet",
        "status": "unknown",
        "sources": {}
    }

    # Налаштування проксі для Tor (якщо запущений)
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    } if check_tor() else {}

    try:
        url = f"https://ahmia.fi/search/?q={query}"
        resp = safe_request(
            url,
            proxies=proxies,
            timeout=config.get("timeout", 15)
        )

        if resp and resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.find_all('a', href=True)
            onion_links = [a['href'] for a in links if '.onion' in a['href']]

            result["sources"]["ahmia"] = {
                "status": "found" if onion_links else "clean",
                "results": onion_links[:10],
                "count": len(onion_links)
            }
            result["status"] = "found" if onion_links else "clean"
        else:
            result["sources"]["ahmia"] = {
                "status": "error",
                "error": f"HTTP {resp.status_code if resp else 'unknown'}"
            }
            result["status"] = "error"

    except Exception as e:
        result["sources"]["ahmia"] = {"status": "error", "error": str(e)}
        result["status"] = "error"

    return result

def check_tor():
    """Перевіряє, чи запущено Tor на локальному порту 9050."""
    try:
        requests.get('http://127.0.0.1:9050', timeout=1)
        return True
    except:
        return False
