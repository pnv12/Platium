import concurrent.futures
import requests
from platium.utils.network import safe_request
from platium.core.config import get_user_agent
from platium.core.errors import ScannerError

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
    "Dev.to": "https://dev.to/{}"
}

def search(username, config, verbose=False):
    """Пошук нікнейму на 80+ платформах"""
    results = {}
    headers = {"User-Agent": get_user_agent()}
    
    def check_platform(name, url):
        try:
            resp = safe_request(url.format(username), headers=headers, timeout=config.get("timeout", 10))
            if resp and resp.status_code == 200:
                return (name, {"found": True, "url": url.format(username)})
            else:
                return (name, {"found": False, "url": url.format(username)})
        except Exception as e:
            return (name, {"found": "Error", "error": str(e)})
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_platform, name, url): name for name, url in PLATFORMS.items()}
        for future in concurrent.futures.as_completed(futures):
            name, result = future.result()
            results[name] = result
    
    return results
