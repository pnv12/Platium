"""
Darknet Scanner — пошук у даркнеті через Ahmia (з опціональним Tor)
"""

import requests
from platium.core.result import ScanResult, ScanStatus
from platium.core.config import load_config
from platium.utils.network import safe_request
from platium.core.errors import ScannerError, NetworkError

AHMIA_URL = "https://ahmia.fi/search/?q={}"

def _check_tor():
    """Перевіряє, чи доступний Tor через SOCKS5-проксі"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 9050))
        sock.close()
        return result == 0
    except:
        return False

def search(query, config=None, verbose=False) -> ScanResult:
    """
    Пошук .onion-посилань через Ahmia.
    Якщо Tor доступний — використовує його, інакше — звичайний HTTP.
    Повертає ScanResult з єдиним контрактом.
    """
    if config is None:
        config = load_config()

    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND
    errors = []

    # Перевіряємо Tor
    tor_available = _check_tor()
    sources["tor"] = {"status": "available" if tor_available else "unavailable"}

    # Налаштовуємо проксі, якщо Tor доступний
    proxies = None
    if tor_available:
        proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050"
        }

    # Запит до Ahmia
    try:
        url = AHMIA_URL.format(query)
        resp = safe_request(url, proxies=proxies, timeout=config.get("timeout", 15))

        if resp is None:
            sources["ahmia"] = {"status": "error", "message": "No response from Ahmia"}
            errors.append("Ahmia: no response")
        elif resp.status_code != 200:
            sources["ahmia"] = {
                "status": "error",
                "code": resp.status_code,
                "message": f"Ahmia returned HTTP {resp.status_code}"
            }
            errors.append(f"Ahmia: HTTP {resp.status_code}")
        else:
            # Парсимо HTML
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '.onion' in href and not href.startswith('/'):
                        links.append(href)

                if links:
                    sources["ahmia"] = {"status": "success", "count": len(links), "results": links[:10]}
                    data["results"] = links[:10]
                    status = ScanStatus.SUCCESS
                else:
                    sources["ahmia"] = {"status": "not_found", "message": "No .onion links found"}
            except ImportError:
                sources["ahmia"] = {"status": "error", "message": "BeautifulSoup not installed"}
                errors.append("Ahmia: BeautifulSoup missing")
            except Exception as e:
                sources["ahmia"] = {"status": "error", "message": str(e)}
                errors.append(f"Ahmia: {str(e)}")

    except Exception as e:
        sources["ahmia"] = {"status": "error", "message": str(e)}
        errors.append(f"Ahmia: {str(e)}")

    # Якщо всі джерела помилкові — статус ERROR
    if status == ScanStatus.NOT_FOUND and errors:
        status = ScanStatus.ERROR

    # Якщо є помилки, але є й успішні джерела — PARTIAL
    if status == ScanStatus.SUCCESS and errors:
        status = ScanStatus.PARTIAL

    # Створюємо результат
    result = ScanResult(
        target=query,
        scanner="darknet",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.9 if status == ScanStatus.SUCCESS else 0.1,
        evidence=[f"Checked Ahmia via {'Tor' if tor_available else 'HTTP'}"]
    )

    return result
