"""
Social Scanner — пошук профілів у соцмережах (без Nitter)
"""

import requests
from platium.core.config import load_config
from platium.utils.network import safe_request
from platium.core.errors import ScannerError

# Реальні соцмережі з перевіркою існування профілю
SOCIAL_PLATFORMS = {
    "Instagram": "https://www.instagram.com/{}/",
    "VK": "https://vk.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "YouTube": "https://www.youtube.com/@{0}",
    "Twitter": "https://twitter.com/{}",
    "Facebook": "https://www.facebook.com/{}",
    "GitHub": "https://github.com/{}",
    "Steam": "https://steamcommunity.com/id/{}",
}

def search(username, config=None, verbose=False):
    """
    Пошук профілів у соцмережах.
    Повертає структурований результат з детальними статусами.
    """
    if config is None:
        config = load_config()

    result = {
        "target": username,
        "scan_type": "social",
        "sources": {},
        "status": "empty"
    }

    timeout = config.get("timeout", 10)
    headers = {"User-Agent": "Mozilla/5.0"}

    for name, url_template in SOCIAL_PLATFORMS.items():
        url = url_template.format(username)
        try:
            resp = safe_request(url, headers=headers, timeout=timeout)
            if resp is None:
                result["sources"][name] = {"status": "skipped", "message": "No response"}
                continue

            if resp.status_code in (301, 302, 303, 307, 308):
                # Редирект на сторінку пошуку або на профіль
                location = resp.headers.get("Location", "")
                if "/search/" in location or "/login" in location:
                    result["sources"][name] = {"status": "not_found", "code": resp.status_code}
                else:
                    result["sources"][name] = {"status": "found", "url": url, "code": resp.status_code}
            elif resp.status_code == 200:
                # Перевіряємо, чи це не сторінка пошуку або помилки
                text_lower = resp.text.lower()
                if "not found" in text_lower or "doesn't exist" in text_lower:
                    result["sources"][name] = {"status": "not_found", "code": 200}
                elif "page not found" in text_lower or "sorry, this page isn't available" in text_lower:
                    result["sources"][name] = {"status": "not_found", "code": 200}
                else:
                    result["sources"][name] = {"status": "found", "url": url, "code": 200}
            elif resp.status_code == 404:
                result["sources"][name] = {"status": "not_found", "code": 404}
            elif resp.status_code == 429:
                result["sources"][name] = {"status": "rate_limited", "message": "Too many requests", "code": 429}
            else:
                result["sources"][name] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
        except Exception as e:
            result["sources"][name] = {"status": "error", "message": str(e)}

    # Загальний статус
    found_count = sum(1 for s in result["sources"].values() if s.get("status") == "found")
    if found_count > 0:
        result["status"] = "success"
    elif any(s.get("status") in ("error", "rate_limited") for s in result["sources"].values()):
        result["status"] = "partial"
    else:
        result["status"] = "empty"

    return result
