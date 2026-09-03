"""
Username Scanner — пошук нікнейму на реально робочих платформах (~30)
"""

import concurrent.futures
from platium.core.config import get_user_agent
from platium.utils.network import safe_request
from platium.core.errors import ScannerError

# Реальні платформи, які коректно реагують на неіснуючі юзернейми (404 або редирект)
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

def search(username, config=None, verbose=False):
    """
    Пошук нікнейму на ~30 платформах.
    Повертає структурований результат з детальними статусами.
    """
    if config is None:
        from platium.core.config import load_config
        config = load_config()

    results = {"target": username, "scan_type": "username", "sources": {}}
    headers = {"User-Agent": get_user_agent()}
    timeout = config.get("timeout", 10)

    def check_platform(name, url):
        try:
            resp = safe_request(url.format(username), headers=headers, timeout=timeout)
            if resp is None:
                return (name, {"status": "error", "message": "No response"})
            if resp.status_code in (301, 302, 303, 307, 308):
                return (name, {"status": "redirect", "url": resp.headers.get("Location", "unknown"), "code": resp.status_code})
            if resp.status_code == 200:
                # Перевіряємо, чи це не сторінка пошуку або помилка
                if "not found" in resp.text.lower() or "doesn't exist" in resp.text.lower():
                    return (name, {"status": "not_found", "code": 200})
                return (name, {"status": "found", "url": url.format(username), "code": 200})
            elif resp.status_code == 404:
                return (name, {"status": "not_found", "code": 404})
            elif resp.status_code == 429:
                return (name, {"status": "rate_limited", "message": "Too many requests", "code": 429})
            else:
                return (name, {"status": "error", "code": resp.status_code, "message": "HTTP error"})
        except Exception as e:
            return (name, {"status": "error", "message": str(e)})

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_platform, name, url): name for name, url in PLATFORMS.items()}
        for future in concurrent.futures.as_completed(futures):
            name, result = future.result()
            results["sources"][name] = result

    # Загальний статус
    found_count = sum(1 for s in results["sources"].values() if s.get("status") == "found")
    if found_count > 0:
        results["status"] = "success"
    elif any(s.get("status") in ("error", "rate_limited") for s in results["sources"].values()):
        results["status"] = "partial"
    else:
        results["status"] = "empty"

    return results
