"""
Social Scanner — пошук профілів у соцмережах (оновлена версія)
"""

import requests
from platium.core.result import ScanResult, ScanStatus
from platium.core.config import load_config
from platium.utils.network import safe_request

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

def search(username, config=None, verbose=False) -> ScanResult:
    """
    Пошук профілів у соцмережах.
    Повертає ScanResult з єдиним контрактом.
    """
    if config is None:
        config = load_config()

    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND
    errors = []

    timeout = config.get("timeout", 10)
    headers = {"User-Agent": "Mozilla/5.0"}

    for name, url_template in SOCIAL_PLATFORMS.items():
        url = url_template.format(username)
        try:
            resp = safe_request(url, headers=headers, timeout=timeout)
            if resp is None:
                sources[name] = {"status": "error", "message": "No response"}
                errors.append(f"{name}: no response")
                continue

            if resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("Location", "")
                if "/search/" in location or "/login" in location:
                    sources[name] = {"status": "not_found", "code": resp.status_code}
                else:
                    sources[name] = {"status": "found", "url": url, "code": resp.status_code}
                    data[name] = {"url": url, "status": "found"}
                    if status != ScanStatus.SUCCESS:
                        status = ScanStatus.SUCCESS
            elif resp.status_code == 200:
                text_lower = resp.text.lower()
                if "not found" in text_lower or "doesn't exist" in text_lower:
                    sources[name] = {"status": "not_found", "code": 200}
                elif "page not found" in text_lower or "sorry, this page isn't available" in text_lower:
                    sources[name] = {"status": "not_found", "code": 200}
                else:
                    sources[name] = {"status": "found", "url": url, "code": 200}
                    data[name] = {"url": url, "status": "found"}
                    if status != ScanStatus.SUCCESS:
                        status = ScanStatus.SUCCESS
            elif resp.status_code == 404:
                sources[name] = {"status": "not_found", "code": 404}
            elif resp.status_code == 429:
                sources[name] = {"status": "rate_limited", "message": "Too many requests", "code": 429}
                errors.append(f"{name}: rate limited")
            else:
                sources[name] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
                errors.append(f"{name}: HTTP {resp.status_code}")
        except Exception as e:
            sources[name] = {"status": "error", "message": str(e)}
            errors.append(f"{name}: {str(e)}")

    # Якщо всі джерела помилкові або rate limited — статус ERROR
    if status == ScanStatus.NOT_FOUND and errors:
        status = ScanStatus.ERROR if len(errors) == len(SOCIAL_PLATFORMS) else ScanStatus.PARTIAL

    # Якщо є помилки, але є й успішні джерела — PARTIAL
    if status == ScanStatus.SUCCESS and errors:
        status = ScanStatus.PARTIAL

    # Створюємо результат
    result = ScanResult(
        target=username,
        scanner="social",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.85 if status == ScanStatus.SUCCESS else 0.2,
        evidence=[f"Checked {len(SOCIAL_PLATFORMS)} platforms"]
    )

    return result
