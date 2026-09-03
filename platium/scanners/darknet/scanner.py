"""
Darknet Scanner — пошук .onion сайтів через Ahmia (з підтримкою Tor)
"""

import requests
from platium.core.config import load_config
from platium.core.errors import ScannerError
from platium.utils.network import safe_request

def check_tor():
    """
    Перевіряє, чи доступний Tor-проксі (127.0.0.1:9050).
    Повертає True, якщо Tor працює і SOCKS5-проксі доступний.
    """
    try:
        # Перевіряємо через запит до Tor-проксі
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        # Робимо запит до check.torproject.org через Tor
        response = requests.get(
            'https://check.torproject.org/',
            proxies=proxies,
            timeout=5
        )
        # Якщо статус 200 і є ознаки Tor — повертаємо True
        if response.status_code == 200 and 'Congratulations' in response.text:
            return True
    except:
        pass
    return False

def search(query, config=None, verbose=False):
    """
    Пошук у даркнеті через Ahmia (з Tor або без).
    """
    if config is None:
        config = load_config()

    result = {
        "target": query,
        "scan_type": "darknet",
        "sources": {},
        "status": "empty"
    }

    # Перевіряємо, чи доступний Tor
    tor_available = check_tor()
    if verbose:
        print(f"[*] Tor available: {tor_available}")

    # Вибираємо проксі (якщо Tor доступний)
    proxies = None
    if tor_available:
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }

    # Запит до Ahmia
    try:
        url = f"https://ahmia.fi/search/?q={query}"
        response = requests.get(url, proxies=proxies, timeout=config.get("timeout", 15))
        if response.status_code == 200:
            # Простий парсинг результатів (без BeautifulSoup)
            results_list = []
            for line in response.text.split('\n'):
                if '.onion' in line:
                    # Шукаємо посилання .onion
                    start = line.find('href="')
                    if start != -1:
                        start += 6
                        end = line.find('"', start)
                        if end != -1:
                            link = line[start:end]
                            if '.onion' in link:
                                results_list.append(link)
            # Унікальні результати (без дублікатів)
            unique_results = list(dict.fromkeys(results_list))
            result["sources"]["ahmia"] = {
                "status": "success",
                "url": url,
                "results": unique_results[:10],  # максимум 10 посилань
                "tor_used": tor_available
            }
            result["status"] = "success" if unique_results else "empty"
        else:
            result["sources"]["ahmia"] = {
                "status": "error",
                "code": response.status_code,
                "message": "HTTP error"
            }
            result["status"] = "error"
    except Exception as e:
        result["sources"]["ahmia"] = {
            "status": "error",
            "message": str(e)
        }
        result["status"] = "error"

    return result
