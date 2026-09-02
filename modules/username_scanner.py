"""
Username Scanner — 80+ платформ
"""

import requests
import concurrent.futures

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "VK": "https://vk.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "YouTube": "https://www.youtube.com/@{0}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "TikTok": "https://www.tiktok.com/@{0}",
    "Medium": "https://medium.com/@{0}",
    "Telegram": "https://t.me/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Flickr": "https://www.flickr.com/people/{}",
    "Vimeo": "https://vimeo.com/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Patreon": "https://www.patreon.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}/",
    "Gravatar": "https://en.gravatar.com/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "ProductHunt": "https://www.producthunt.com/@{0}",
    "Keybase": "https://keybase.io/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Replit": "https://replit.com/@{}",
    "Dev.to": "https://dev.to/{}",
    "Gist": "https://gist.github.com/{}",
}

def check_platform(url, username):
    """Перевіряє одну платформу"""
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def search(username):
    """Пошук нікнейму на 80+ платформах"""
    results = {}
    urls = {name: url.format(username) for name, url in PLATFORMS.items()}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(check_platform, url, username): name for name, url in urls.items()}
        for future in concurrent.futures.as_completed(future_to_url):
            name = future_to_url[future]
            urls[name] = urls[name]  # зберігаємо URL
            try:
                found = future.result()
                results[name] = {"found": found, "url": urls[name]}
            except:
                results[name] = {"found": "Помилка", "url": urls[name]}
    
    return results
