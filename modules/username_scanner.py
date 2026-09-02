"""
Username Scanner — 60+ платформ
"""

import requests
import json

def search(username):
    """Пошук нікнейму на популярних платформах"""
    results = {}
    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "VK": f"https://vk.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "Pinterest": f"https://www.pinterest.com/{username}/",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Medium": f"https://medium.com/@{username}",
        "Telegram": f"https://t.me/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
    }
    
    for name, url in platforms.items():
        try:
            response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                results[name] = {"found": True, "url": url}
            else:
                results[name] = {"found": False, "url": url}
        except:
            results[name] = {"found": "Помилка", "url": url}
    
    return results
