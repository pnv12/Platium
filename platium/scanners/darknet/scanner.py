import requests
from bs4 import BeautifulSoup
from platium.core.result import ScanResult, ScanStatus
from platium.core.config import config
from platium.utils.url_validation import is_safe_url

AHMIA_URL = "https://ahmia.fi/search/?q={}"

def _check_tor():
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 9050))
        sock.close()
        return result == 0
    except:
        return False

def search(query, verbose=False) -> ScanResult:
    """
    Пошук .onion-посилань через Ahmia.
    Повертає ScanResult.
    """
    sources = {}
    data = {}
    errors = []
    status = ScanStatus.NOT_FOUND

    tor_available = _check_tor()
    sources["tor"] = {"status": "available" if tor_available else "unavailable"}

    proxies = None
    if tor_available:
        proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050"
        }

    try:
        url = AHMIA_URL.format(query)
        if not is_safe_url(url):
            return ScanResult.error_result(
                target=query,
                scanner="darknet",
                error="URL validation failed"
            )

        resp = requests.get(url, proxies=proxies, timeout=config.timeout)
        if resp.status_code != 200:
            sources["ahmia"] = {"status": "error", "code": resp.status_code}
            return ScanResult(
                target=query,
                scanner="darknet",
                status=ScanStatus.ERROR,
                sources=sources,
                error=f"Ahmia returned HTTP {resp.status_code}"
            )

        soup = BeautifulSoup(resp.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.onion' in href and not href.startswith('/'):
                links.append(href)

        if links:
            data["results"] = links[:10]
            sources["ahmia"] = {"status": "success", "count": len(links)}
            status = ScanStatus.SUCCESS
        else:
            sources["ahmia"] = {"status": "not_found"}
            status = ScanStatus.NOT_FOUND

    except Exception as e:
        return ScanResult.error_result(
            target=query,
            scanner="darknet",
            error=str(e)
        )

    return ScanResult(
        target=query,
        scanner="darknet",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.8 if status == ScanStatus.SUCCESS else 0.1,
        evidence=[f"Found {len(links)} .onion links"] if links else []
    )
