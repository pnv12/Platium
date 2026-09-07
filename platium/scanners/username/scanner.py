import concurrent.futures
from platium.core.config import load_config
from platium.core.result import ScanResult, ScanStatus
from platium.utils.http_client import get_http_client

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "VK": "https://vk.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "YouTube": "https://www.youtube.com/@{0}",
    "TikTok": "https://www.tiktok.com/@{0}",
    "Telegram": "https://t.me/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Flickr": "https://www.flickr.com/people/{}",
    "Vimeo": "https://vimeo.com/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Patreon": "https://www.patreon.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}/",
    "Gravatar": "https://en.gravatar.com/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "Keybase": "https://keybase.io/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Dev.to": "https://dev.to/{}",
    "Medium": "https://medium.com/@{0}",
    "ProductHunt": "https://www.producthunt.com/@{0}",
    "Replit": "https://replit.com/@{}",
    "Gist": "https://gist.github.com/{}",
    "HackTheBox": "https://www.hackthebox.com/profile/{}",
    "TryHackMe": "https://tryhackme.com/p/{}",
}

def search(username, config=None, verbose=False) -> ScanResult:
    """
    Пошук нікнейму на 30+ платформах.
    Використовує новий HTTP Client з кешуванням.
    Повертає ScanResult.
    """
    if config is None:
        config = load_config()

    client = get_http_client()
    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND
    errors = []
    found_platforms = []

    def check_platform(name, url):
        try:
            resp = client.get(url.format(username), use_cache=True)
            if resp is None:
                return (name, {"status": "error", "message": "No response"})
            if resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("Location", "")
                if "/search/" in location or "/login" in location:
                    return (name, {"status": "not_found", "code": resp.status_code})
                return (name, {"status": "found", "url": url.format(username), "code": resp.status_code})
            if resp.status_code == 200:
                text_lower = resp.text.lower()
                if "not found" in text_lower or "doesn't exist" in text_lower:
                    return (name, {"status": "not_found", "code": 200})
                if "page not found" in text_lower or "sorry, this page isn't available" in text_lower:
                    return (name, {"status": "not_found", "code": 200})
                return (name, {"status": "found", "url": url.format(username), "code": 200})
            if resp.status_code == 404:
                return (name, {"status": "not_found", "code": 404})
            if resp.status_code == 429:
                return (name, {"status": "rate_limited", "code": 429})
            return (name, {"status": "error", "code": resp.status_code})
        except Exception as e:
            return (name, {"status": "error", "message": str(e)})

    max_workers = config.get("max_workers", 20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_platform, name, url): name for name, url in PLATFORMS.items()}
        for future in concurrent.futures.as_completed(futures):
            name, result = future.result()
            sources[name] = result
            if result.get("status") == "found":
                found_platforms.append(name)
                data[name] = {"url": result.get("url"), "status": "found"}

    if found_platforms:
        status = ScanStatus.SUCCESS
        confidence = min(0.9, 0.5 + 0.05 * len(found_platforms))
    elif any(s.get("status") in ("error", "rate_limited") for s in sources.values()):
        status = ScanStatus.PARTIAL
        confidence = 0.2
    else:
        status = ScanStatus.NOT_FOUND
        confidence = 0.0

    for name, result in sources.items():
        if result.get("status") in ("error", "rate_limited"):
            errors.append(f"{name}: {result.get('message', 'Unknown error')}")

    return ScanResult(
        target=username,
        scanner="username",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=confidence,
        evidence=[f"Found on {len(found_platforms)} platforms"] if found_platforms else [],
    )
